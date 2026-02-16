#!/bin/bash
set -e

# Run data ingestion if SQLite DB doesn't exist yet
if [ ! -f /app/backend/bigspring.db ]; then
    echo "Running initial data ingestion..."
    uv run python run_ingestion.py
    echo "Ingestion complete."
fi

# Start FastAPI server
exec uv run uvicorn main:app --host 0.0.0.0 --port 8000
