import os
from pathlib import Path
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent
BASE_DIR = BACKEND_DIR.parent

load_dotenv(BACKEND_DIR / ".env")
DATABASE_DIR = BASE_DIR / "resources" / "database"
ASSETS_DIR = BASE_DIR / "resources" / "assets"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
CHROMA_PERSIST_DIR = str(BASE_DIR / "backend" / "chroma_db")
SQLITE_DB_PATH = str(BASE_DIR / "backend" / "bigspring.db")

EMBEDDING_MODEL = "text-embedding-3-small"
CLASSIFIER_MODEL = "gpt-4o-mini"
ANSWER_MODEL = "gpt-4o"

KNOWLEDGE_TOP_K = 8
HISTORY_TOP_K = 6
