import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from database.models import SessionLocal, Company, User, Play, PlayAssignment
from services.auth import get_user
from services.streaming import sse_event
from search.router import classify_intent
from search.knowledge import search_knowledge, generate_knowledge_answer
from search.history import search_history, generate_history_answer
from search.fallback import generate_fallback_answer, DISCLAIMER
from search.guardrails import OUT_OF_SCOPE_MESSAGE, NO_RESULTS_MESSAGE
from services.recommendations import get_recommendations

app = FastAPI(title="BigSpring Knowledge Search Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/companies")
def list_companies():
    session = SessionLocal()
    companies = session.query(Company).all()
    result = [{"id": c.id, "name": c.name, "description": c.description} for c in companies]
    session.close()
    return result


@app.get("/api/companies/{company_id}/users")
def list_users(company_id: str):
    session = SessionLocal()
    users = session.query(User).filter(User.company_id == company_id).order_by(User.username).all()
    result = [{
        "id": u.id, "username": u.username, "display_name": u.display_name,
        "role": u.role, "segment": u.segment, "is_active": u.is_active,
    } for u in users]
    session.close()
    return result


@app.get("/api/users/{user_id}")
def get_user_detail(user_id: str):
    session = SessionLocal()
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        session.close()
        raise HTTPException(status_code=404, detail="User not found")

    assignments = session.query(PlayAssignment).filter(PlayAssignment.user_id == user_id).all()
    plays_info = []
    for a in assignments:
        play = session.query(Play).filter(Play.id == a.play_id).first()
        if play:
            plays_info.append({
                "play_id": play.id, "title": play.title,
                "status": a.status, "assigned_date": a.assigned_date,
            })

    result = {
        "id": user.id, "username": user.username, "display_name": user.display_name,
        "company_id": user.company_id, "role": user.role, "segment": user.segment,
        "assigned_plays": plays_info,
    }
    session.close()
    return result


class SearchRequest(BaseModel):
    user_id: str
    query: str


@app.post("/api/search")
async def search(request: SearchRequest):
    user = get_user(request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    async def event_generator():
        query = request.query
        company_id = user["company_id"]
        user_id = user["id"]

        # Step 1: Classify intent
        intent_result = classify_intent(query)
        intent = intent_result["intent"]
        reasoning = intent_result["reasoning"]

        yield sse_event("intent", {"intent": intent, "reasoning": reasoning})

        # Step 2: Handle based on intent
        if intent == "OUT_OF_SCOPE":
            yield sse_event("answer_chunk", {"text": OUT_OF_SCOPE_MESSAGE})
            yield sse_event("done", {"status": "complete"})
            return

        if intent == "GENERAL_PROFESSIONAL":
            yield sse_event("answer_chunk", {"text": DISCLAIMER})
            stream = generate_fallback_answer(query)
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield sse_event("answer_chunk", {"text": chunk.choices[0].delta.content})
            yield sse_event("done", {"status": "complete"})
            return

        if intent == "HISTORY_SEARCH":
            result = search_history(query, user_id, company_id)
            if result["no_results"]:
                yield sse_event("answer_chunk", {
                    "text": "I couldn't find any matching content in your practice submissions. "
                    "Make sure you've completed practice reps with submissions to search through."
                })
                yield sse_event("done", {"status": "complete"})
                return

            yield sse_event("citations", {"citations": result["citations"]})

            stream = generate_history_answer(query, result["context"], result["citations"])
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield sse_event("answer_chunk", {"text": chunk.choices[0].delta.content})

            # Get recommendations
            try:
                recs = get_recommendations(query, user_id, company_id)
                if recs:
                    yield sse_event("recommendations", {"recommendations": recs})
            except Exception:
                pass

            yield sse_event("done", {"status": "complete"})
            return

        # KNOWLEDGE_SEARCH (default)
        result = search_knowledge(query, user_id, company_id)
        if result["no_results"]:
            yield sse_event("answer_chunk", {"text": NO_RESULTS_MESSAGE})
            yield sse_event("done", {"status": "complete"})
            return

        yield sse_event("citations", {"citations": result["citations"]})

        stream = generate_knowledge_answer(query, result["context"], result["citations"])
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield sse_event("answer_chunk", {"text": chunk.choices[0].delta.content})

        # Get recommendations (excluding already-cited assets)
        try:
            cited_assets = {c.get("source_file", "").replace(".json", "") for c in result["citations"]}
            recs = get_recommendations(query, user_id, company_id)
            if recs:
                yield sse_event("recommendations", {"recommendations": recs})
        except Exception:
            pass

        yield sse_event("done", {"status": "complete"})

    return EventSourceResponse(event_generator())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
