import chromadb
from openai import OpenAI
from config import CHROMA_PERSIST_DIR, OPENAI_API_KEY, EMBEDDING_MODEL
from services.auth import get_user_accessible_asset_ids
from database.models import SessionLocal, Asset, Rep, Play

client = OpenAI(api_key=OPENAI_API_KEY)


def get_recommendations(query: str, user_id: str, company_id: str, exclude_asset_ids: set[str] = None) -> list[dict]:
    accessible_asset_ids = get_user_accessible_asset_ids(user_id)
    if not accessible_asset_ids:
        return []

    if exclude_asset_ids:
        search_ids = accessible_asset_ids - exclude_asset_ids
    else:
        search_ids = accessible_asset_ids

    if not search_ids:
        return []

    chroma = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    collection = chroma.get_collection("knowledge")

    resp = client.embeddings.create(input=[query[:8000]], model=EMBEDDING_MODEL)
    query_embedding = resp.data[0].embedding

    where_filter = {
        "$and": [
            {"company_id": {"$eq": company_id}},
            {"asset_id": {"$in": list(search_ids)}},
        ]
    }

    results = collection.query(
        query_embeddings=[query_embedding],
        where=where_filter,
        n_results=5,
        include=["metadatas", "distances"],
    )

    if not results["metadatas"] or not results["metadatas"][0]:
        return []

    # Deduplicate by asset_id and map to reps/plays
    seen_assets = set()
    recommendations = []
    session = SessionLocal()

    for meta, dist in zip(results["metadatas"][0], results["distances"][0]):
        asset_id = meta.get("asset_id", "")
        if asset_id in seen_assets:
            continue
        seen_assets.add(asset_id)

        asset = session.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            continue

        rep = session.query(Rep).filter(Rep.asset_id == asset_id).first()
        if not rep:
            continue

        play = session.query(Play).filter(Play.id == rep.play_id).first()

        recommendations.append({
            "asset_id": asset_id,
            "asset_type": asset.type,
            "rep_title": rep.prompt_title,
            "play_title": play.title if play else "",
            "file_name": asset.file_name,
            "relevance": round(1 - dist, 3),
        })

        if len(recommendations) >= 3:
            break

    session.close()
    return recommendations
