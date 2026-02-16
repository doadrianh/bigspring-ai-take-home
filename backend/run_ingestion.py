#!/usr/bin/env python3
"""Run data loading and vector ingestion pipeline."""
import sys

from config import OPENAI_API_KEY

if not OPENAI_API_KEY or OPENAI_API_KEY == "your-openai-api-key-here":
    print("ERROR: Please set OPENAI_API_KEY in backend/.env file before running ingestion.")
    print("Edit backend/.env and replace 'your-openai-api-key-here' with your actual key.")
    sys.exit(1)

print("=" * 60)
print("BigSpring Knowledge Search - Data Ingestion Pipeline")
print("=" * 60)

print("\nStep 1: Loading CSV/JSON data into SQLite...")
from database.init_db import load_all
load_all()

print("\nStep 2: Ingesting assets into ChromaDB with embeddings...")
from ingestion.ingest import run_ingestion
run_ingestion()

print("\n" + "=" * 60)
print("Ingestion complete! You can now start the servers:")
print("  Backend:  cd backend && uv run uvicorn main:app --reload")
print("  Frontend: cd frontend && npm run dev")
print("=" * 60)
