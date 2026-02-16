import chromadb
from openai import OpenAI
from config import CHROMA_PERSIST_DIR, OPENAI_API_KEY, EMBEDDING_MODEL, ANSWER_MODEL, KNOWLEDGE_TOP_K
from services.auth import get_user_accessible_asset_ids
from database.models import SessionLocal, Asset

client = OpenAI(api_key=OPENAI_API_KEY)


def get_embedding(text: str) -> list[float]:
    resp = client.embeddings.create(input=[text[:8000]], model=EMBEDDING_MODEL)
    return resp.data[0].embedding


def search_knowledge(query: str, user_id: str, company_id: str):
    accessible_asset_ids = get_user_accessible_asset_ids(user_id)
    if not accessible_asset_ids:
        return {"chunks": [], "answer": None, "citations": [], "no_results": True}

    chroma = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    collection = chroma.get_collection("knowledge")

    query_embedding = get_embedding(query)

    # ChromaDB where filter: asset_id must be in user's accessible set AND company must match
    where_filter = {
        "$and": [
            {"company_id": {"$eq": company_id}},
            {"asset_id": {"$in": list(accessible_asset_ids)}},
        ]
    }

    results = collection.query(
        query_embeddings=[query_embedding],
        where=where_filter,
        n_results=KNOWLEDGE_TOP_K,
        include=["documents", "metadatas", "distances"],
    )

    if not results["documents"] or not results["documents"][0]:
        return {"chunks": [], "answer": None, "citations": [], "no_results": True}

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    # Build context for answer generation
    context_parts = []
    citations = []
    session = SessionLocal()

    for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
        asset = session.query(Asset).filter(Asset.id == meta.get("asset_id")).first()
        source_name = asset.file_name.replace(".json", "") if asset else meta.get("source_file", "Unknown")
        asset_type = asset.type if asset else "unknown"

        citation = {
            "index": i + 1,
            "source_file": meta.get("source_file", ""),
            "source_name": source_name,
            "asset_type": asset_type,
            "chunk_type": meta.get("chunk_type", ""),
            "relevance": round(1 - dist, 3),
        }

        if meta.get("page"):
            citation["page"] = meta["page"]
        if meta.get("start"):
            citation["start"] = meta["start"]
            citation["end"] = meta.get("end", "")
        if meta.get("speaker"):
            citation["speaker"] = meta["speaker"]
        if meta.get("table_title"):
            citation["table_title"] = meta["table_title"]

        citations.append(citation)
        # Format context block
        label = f"[Source {i+1}: {source_name}"
        if meta.get("page"):
            label += f", Page {meta['page']}"
        if meta.get("start"):
            label += f", {meta['start']}-{meta.get('end', '')}"
        label += "]"
        context_parts.append(f"{label}\n{doc}")

    session.close()

    context = "\n\n---\n\n".join(context_parts)
    return {"chunks": documents, "context": context, "citations": citations, "no_results": False}


def generate_knowledge_answer(query: str, context: str, citations: list[dict]):
    system = """You are a helpful search assistant for BigSpring, a sales training platform.
Answer the user's question using ONLY the provided source materials. Be precise and cite specific data points.

Rules:
- Reference sources using [Source N] notation
- If the information includes tables, present data clearly
- If you find specific numbers, dates, or metrics, state them exactly
- Be concise but thorough
- Do NOT make up information not present in the sources
- If the sources don't contain the specific product/topic asked about, clearly state that it was not found in the user's assigned materials. Then, if the sources contain related or similar information (e.g. dosage info for a different product), proactively share that as a helpful alternative."""

    user_msg = f"Question: {query}\n\nSource Materials:\n{context}"

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
