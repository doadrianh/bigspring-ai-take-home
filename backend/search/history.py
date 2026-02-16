import chromadb
from openai import OpenAI
from config import CHROMA_PERSIST_DIR, OPENAI_API_KEY, EMBEDDING_MODEL, ANSWER_MODEL, HISTORY_TOP_K
from services.auth import get_user_submission_asset_ids, get_user_submissions_with_feedback

client = OpenAI(api_key=OPENAI_API_KEY)


def get_embedding(text: str) -> list[float]:
    resp = client.embeddings.create(input=[text[:8000]], model=EMBEDDING_MODEL)
    return resp.data[0].embedding


def search_history(query: str, user_id: str, company_id: str):
    submission_asset_ids = get_user_submission_asset_ids(user_id)
    if not submission_asset_ids:
        return {"chunks": [], "answer": None, "citations": [], "no_results": True}

    chroma = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    collection = chroma.get_collection("submissions")

    query_embedding = get_embedding(query)

    where_filter = {
        "$and": [
            {"user_id": {"$eq": user_id}},
            {"asset_id": {"$in": list(submission_asset_ids)}},
        ]
    }

    results = collection.query(
        query_embeddings=[query_embedding],
        where=where_filter,
        n_results=HISTORY_TOP_K,
        include=["documents", "metadatas", "distances"],
    )

    if not results["documents"] or not results["documents"][0]:
        return {"chunks": [], "answer": None, "citations": [], "no_results": True}

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    # Get feedback context
    submissions_with_feedback = get_user_submissions_with_feedback(user_id)
    feedback_map = {s["asset_id"]: s for s in submissions_with_feedback}

    context_parts = []
    citations = []

    for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
        asset_id = meta.get("asset_id", "")
        sub_info = feedback_map.get(asset_id, {})

        citation = {
            "index": i + 1,
            "source_file": meta.get("source_file", ""),
            "source_name": f"Your submission: {sub_info.get('rep_title', 'Practice')}",
            "asset_type": "submission",
            "chunk_type": meta.get("chunk_type", ""),
            "submission_id": meta.get("submission_id", ""),
            "relevance": round(1 - dist, 3),
        }
        if meta.get("start"):
            citation["start"] = meta["start"]
            citation["end"] = meta.get("end", "")
        if sub_info.get("feedback_score") is not None:
            citation["feedback_score"] = sub_info["feedback_score"]
            citation["feedback_text"] = sub_info.get("feedback_text", "")

        citations.append(citation)

        label = f"[Submission {i+1}: {sub_info.get('rep_title', 'Practice')}"
        if meta.get("start"):
            label += f", {meta['start']}-{meta.get('end', '')}"
        label += "]"

        feedback_note = ""
        if sub_info.get("feedback_score") is not None:
            feedback_note = f"\nFeedback (Score {sub_info['feedback_score']}/10): {sub_info.get('feedback_text', '')}"

        context_parts.append(f"{label}\n{doc}{feedback_note}")

    context = "\n\n---\n\n".join(context_parts)
    return {"chunks": documents, "context": context, "citations": citations, "no_results": False}


def generate_history_answer(query: str, context: str, citations: list[dict]):
    system = """You are a helpful search assistant for BigSpring, a sales training platform.
The user is asking about their OWN past practice submissions and feedback.
Answer using ONLY the provided submission transcripts and feedback data.

Rules:
- Reference submissions using [Submission N] notation
- Include specific timestamps when available (e.g., "at 00:23-00:35")
- Mention feedback scores and coaching comments when relevant
- Be supportive and constructive in tone
- Do NOT make up information not present in the sources"""

    user_msg = f"Question: {query}\n\nYour Submissions & Feedback:\n{context}"

    stream = client.chat.completions.create(
        model=ANSWER_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.1,
        stream=True,
    )
    return stream
