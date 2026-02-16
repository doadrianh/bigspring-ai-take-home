import json
import shutil
from pathlib import Path
import chromadb
from openai import OpenAI
from config import ASSETS_DIR, CHROMA_PERSIST_DIR, EMBEDDING_MODEL, OPENAI_API_KEY
from database.models import SessionLocal, Asset, Submission
from ingestion.chunker import chunk_asset

client = OpenAI(api_key=OPENAI_API_KEY)


def get_embedding(text: str) -> list[float]:
    text = text[:8000]
    resp = client.embeddings.create(input=[text], model=EMBEDDING_MODEL)
    return resp.data[0].embedding


def run_ingestion():
    # Clean up old data
    chroma_path = Path(CHROMA_PERSIST_DIR)
    if chroma_path.exists():
        shutil.rmtree(chroma_path)

    chroma = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    knowledge_col = chroma.get_or_create_collection("knowledge", metadata={"hnsw:space": "cosine"})
    submissions_col = chroma.get_or_create_collection("submissions", metadata={"hnsw:space": "cosine"})

    session = SessionLocal()

    submission_map = {}
    for sub in session.query(Submission).all():
        submission_map[sub.asset_id] = (sub.user_id, sub.id)

    assets = session.query(Asset).all()
    print(f"Processing {len(assets)} assets...")

    knowledge_count = 0
    submission_count = 0

    for asset in assets:
        file_path = ASSETS_DIR / asset.file_name
        if not file_path.exists():
            print(f"  Skipping {asset.file_name} (file not found)")
            continue

        with open(file_path) as f:
            data = json.load(f)

        is_submission = asset.id in submission_map
        user_id, submission_id = submission_map.get(asset.id, ("", ""))

        chunks = chunk_asset(
            asset_type=asset.type, data=data,
            asset_id=asset.id, company_id=asset.company_id,
            file_name=asset.file_name,
            user_id=user_id, submission_id=submission_id,
        )

        # Collect chunks for this asset and insert in one batch
        ids, embeddings, documents, metadatas = [], [], [], []
        for i, chunk in enumerate(chunks):
            text = chunk["text"]
            if not text.strip():
                continue
            chunk_id = f"{asset.id}_chunk_{i}"
            embedding = get_embedding(text)
            meta = {k: str(v) for k, v in chunk["metadata"].items()}
            ids.append(chunk_id)
            embeddings.append(embedding)
            documents.append(text)
            metadatas.append(meta)

        if ids:
            target = submissions_col if is_submission else knowledge_col
            target.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
            if is_submission:
                submission_count += len(ids)
            else:
                knowledge_count += len(ids)

        print(f"  Processed {asset.file_name}: {len(ids)} chunks")

    print(f"\nTotal: {knowledge_count} knowledge chunks, {submission_count} submission chunks")
    session.close()
    print("Ingestion complete!")


if __name__ == "__main__":
    from database.init_db import load_all
    print("Step 1: Loading CSV/JSON data into SQLite...")
    load_all()
    print("\nStep 2: Ingesting assets into ChromaDB...")
    run_ingestion()
