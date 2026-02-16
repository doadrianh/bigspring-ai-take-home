.PHONY: install install-backend install-frontend ingest backend frontend dev clean

# Install all dependencies
install: install-backend install-frontend

install-backend:
	cd backend && uv sync

install-frontend:
	cd frontend && npm install

# Load data into SQLite + index into ChromaDB
ingest:
	cd backend && uv run python run_ingestion.py

# Run backend (FastAPI on port 8000)
backend:
	cd backend && uv run uvicorn main:app --reload --port 8000

# Run frontend (Next.js on port 3000)
frontend:
	cd frontend && npm run dev

# Run both backend and frontend concurrently
dev:
	@echo "Starting backend and frontend..."
	@make backend & make frontend

# Remove generated files
clean:
	rm -rf backend/chroma_db/
	rm -f backend/bigspring.db
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Full setup: install deps, ingest data, start app
setup: install ingest dev
