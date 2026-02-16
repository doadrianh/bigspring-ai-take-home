# BigSpring "Knowledge-to-Action" Search Agent

A secure, multi-tenant Generative Search Engine that allows Sales Representatives to retrieve specific data from their assigned training materials and personal performance history. Built as a RAG-powered search system with strict data isolation, intent-based routing, and intelligent guardrails.

## Table of Contents

- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Running the Application](#running-the-application)
- [How It Works](#how-it-works)
- [Guardrails & Fallback Logic](#guardrails--fallback-logic)
- [Test Cases](#test-cases)
- [AI Tools Used](#ai-tools-used)

## Architecture

The system implements a **Router/Agentic Pattern** with intent-based dispatching:

```
User Query
    │
    ▼
┌──────────────────────────┐
│  Intent Classification   │  (gpt-4o-mini, temperature=0)
│  4 categories detected   │
└──────────┬───────────────┘
           │
    ┌──────┼──────────┬────────────────┐
    ▼      ▼          ▼                ▼
┌────────┐┌─────────┐┌──────────────┐┌────────────┐
│OUT_OF_ ││KNOWLEDGE││HISTORY_      ││GENERAL_    │
│SCOPE   ││_SEARCH  ││SEARCH        ││PROFESSIONAL│
└────┬───┘└────┬────┘└──────┬───────┘└─────┬──────┘
     │         │            │              │
     ▼         ▼            ▼              ▼
 Guardrail  ChromaDB     ChromaDB      LLM General
 Message    (knowledge)  (submissions) Knowledge +
            + gpt-4o     + gpt-4o      Disclaimer
                │            │
                ▼            ▼
          ┌─────────────────────┐
          │   Recommendations   │
          │   (2-3 follow-ups)  │
          └─────────────────────┘
```

**Why this pattern?** A router-first approach prevents hallucination on out-of-scope queries early, keeps retrieval logic modular (knowledge vs. history are separate pipelines), and allows each sub-component to be tuned independently.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend Framework | FastAPI (Python) |
| Relational DB | SQLite (via SQLAlchemy) |
| Vector DB | ChromaDB (persistent, cosine similarity) |
| Embeddings | OpenAI `text-embedding-3-small` |
| LLM (Classification) | `gpt-4o-mini` (temperature=0) |
| LLM (Generation) | `gpt-4o` (temperature=0.1 for knowledge, 0.3 for fallback) |
| Streaming | Server-Sent Events (SSE) via `sse-starlette` |
| Frontend | Next.js 14 + React 18 |
| Markdown Rendering | `react-markdown` |

## Project Structure

```
.
├── backend/
│   ├── main.py                  # FastAPI app, API endpoints
│   ├── config.py                # Model names, top-K, DB paths
│   ├── database/
│   │   ├── models.py            # SQLAlchemy ORM models
│   │   └── init_db.py           # CSV/JSON → SQLite loader
│   ├── ingestion/
│   │   ├── chunker.py           # Asset-type-aware chunking (PDF, video, image, etc.)
│   │   └── ingest.py            # ChromaDB ingestion pipeline
│   ├── search/
│   │   ├── router.py            # Intent classification (4-way)
│   │   ├── guardrails.py        # Guardrail messages & boundary enforcement
│   │   ├── knowledge.py         # Knowledge base retrieval (Watch Reps)
│   │   ├── history.py           # Submission history retrieval (Practice Reps)
│   │   └── fallback.py          # General professional knowledge fallback
│   ├── services/
│   │   ├── auth.py              # User context & permission resolution
│   │   ├── recommendations.py   # Follow-up content recommendations
│   │   └── streaming.py         # SSE event formatting helpers
│   ├── chroma_db/               # Persisted ChromaDB vector store (generated)
│   ├── run_ingestion.py         # One-shot script: load DB + ingest vectors
│   ├── .env.example             # Environment variable template
│   ├── pyproject.toml           # uv project config & dependencies
│   └── uv.lock                  # Lockfile for reproducible installs
├── frontend/
│   ├── src/
│   │   ├── app/page.tsx         # Main search page
│   │   ├── components/
│   │   │   ├── CompanySelector   # Company dropdown
│   │   │   ├── UserSelector      # User dropdown (filtered by company)
│   │   │   ├── SearchBar         # Natural language search input
│   │   │   ├── StreamingAnswer   # Token-by-token answer display
│   │   │   ├── ThoughtTrace      # Collapsible intent/reasoning trace
│   │   │   ├── CitationCard      # Source citations with deep links
│   │   │   └── RecommendationPanel # Related training materials
│   │   └── lib/api.ts           # API client with SSE stream parsing
│   └── package.json
├── resources/
│   ├── database/                # CSV/JSON source data (companies, users, plays, etc.)
│   └── assets/                  # 63 structured JSON files (PDFs, videos, submissions)
└── README.md
```

## Setup & Installation

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Node.js 18+
- An OpenAI API key

### 1. Clone the repository

```bash
git clone <repo-url>
cd BigSpring_AI_take_home
```

### 2. Set up environment variables

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and add your OpenAI API key:

```
OPENAI_API_KEY=your-openai-api-key-here
```

### 3. Install dependencies, ingest data, and start the app

```bash
make setup
```

This single command will install all dependencies, run data ingestion, and start both servers.

Alternatively, run each step individually:

| Command | Description |
|---------|-------------|
| `make install` | Install backend (`uv sync`) and frontend (`npm install`) dependencies |
| `make ingest` | Load CSVs into SQLite + index assets into ChromaDB |
| `make dev` | Start both backend and frontend concurrently |
| `make backend` | Start only the FastAPI backend (port 8000) |
| `make frontend` | Start only the Next.js frontend (port 3000) |
| `make clean` | Remove generated files (ChromaDB, SQLite, `__pycache__`) |

The ingestion step:
- Drops and recreates all SQLite tables from the CSV/JSON files in `resources/database/`
- Chunks all 63 assets (PDFs by page/table, videos by segment, etc.)
- Generates embeddings via `text-embedding-3-small`
- Stores vectors in two ChromaDB collections: `knowledge` and `submissions`

## Running the Application

```bash
make dev
```

This starts both servers concurrently:
- **Backend** (FastAPI): `http://localhost:8000`
- **Frontend** (Next.js): `http://localhost:3000`

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/companies` | List all companies |
| `GET` | `/api/companies/{company_id}/users` | List users in a company |
| `GET` | `/api/users/{user_id}` | Get user details + assigned plays |
| `POST` | `/api/search` | Streaming search (SSE) |

**Search request body:**

```json
{
  "user_id": "user-vel-001",
  "query": "What is the eradication rate for Streptococcus pneumoniae?"
}
```

**SSE response events:**

| Event | Data |
|-------|------|
| `intent` | `{ "intent": "KNOWLEDGE_SEARCH", "reasoning": "..." }` |
| `answer_chunk` | `{ "chunk": "The eradication rate..." }` |
| `citations` | `[{ "source": "amproxin_guide.json", "page": 1, ... }]` |
| `recommendations` | `[{ "rep_title": "...", "play_title": "...", ... }]` |
| `done` | `{}` |

## How It Works

### 1. Context Selection

The user selects a **Company** and then a **User** within that company. This sets the tenant context for all subsequent searches.

### 2. Intent Classification

Every query is classified by `gpt-4o-mini` into one of four intents:

- **KNOWLEDGE_SEARCH** - Query about assigned training materials (Watch Reps)
- **HISTORY_SEARCH** - Query about the user's own practice submissions and feedback
- **GENERAL_PROFESSIONAL** - Professional question not found in assigned materials
- **OUT_OF_SCOPE** - Non-professional, irrelevant query

### 3. Scoped Retrieval

**Data isolation is enforced at the DB level *before* vector search:**

- **Knowledge queries**: Resolve `user → play_assignments → plays → reps (watch) → assets`, then filter ChromaDB by those asset IDs + company ID
- **History queries**: Resolve `user → submissions → assets`, then filter ChromaDB by those asset IDs + user ID

This ensures users can never access content from other companies, unassigned plays, or other users' submissions.

### 4. Answer Generation

Retrieved chunks are passed as grounded context to `gpt-4o` with strict instructions not to hallucinate beyond provided sources. Answers stream token-by-token via SSE.

### 5. Recommendations

After every answer, the system recommends 2-3 follow-up training materials (Reps/Plays) relevant to the query, excluding already-cited sources.

## Guardrails & Fallback Logic

The system implements a **three-tier guardrail strategy**:

| Tier | Trigger | Behavior |
|------|---------|----------|
| **Search Boundary** | Non-professional queries (e.g., "Tell me a joke") | Returns: *"I am a specialized search engine for your assigned BigSpring materials. I cannot assist with queries outside of your professional scope."* |
| **General Professional Fallback** | Professional but not in assigned materials (e.g., "How do I handle price objections?") | Answers using LLM general knowledge with disclaimer: *"This response is based on general sales knowledge and is not found in your assigned company materials."* |
| **Proprietary Data Guardrail** | Specific company data not in user's assigned Plays | Returns: *"I cannot find any specific information in your assigned materials regarding this query."* No hallucination allowed. |

**Conflict Prevention**: Brand-specific data remains isolated. For example, the drug Lydrenex appears in both Veldra (Zaloric) and Aetheris (Nuvia) contexts - the system only returns data from the user's assigned plays, preventing cross-brand leakage.

## Test Cases

### Valid Search (Authorized Access)

| Case | User | Query | Expected |
|------|------|-------|----------|
| PDF Knowledge Search | `aaron-veldra` | "What is the eradication rate for Streptococcus pneumoniae?" | 94.2% with citation `[amproxin_guide.pdf: Page 1]` |
| Video Submission Search | `daphne-kyberon` | "When did I mention cooling energy costs?" | Deep-linked citation `[Video: 00:26 - 00:38]` |

### Invalid Search (Data Isolation)

| Case | User | Query | Expected |
|------|------|-------|----------|
| Cross-Company Leakage | `sophie-aetheris` | "Show me the GridMaster PUE efficiency table." | No results (Kyberon content blocked) |
| Unassigned Play (Same Co.) | `leo-aetheris` | "How does Lydrenex protect the amygdala?" | No results (not assigned to Nuvia play) |
| Peer Submissions | `aaron-veldra` | "Show me Aaron's pitch about antibiotics." | No results (other user's submission) |

### Edge Cases

| Case | User | Query | Expected |
|------|------|-------|----------|
| Shared Ingredient | `aaron-veldra` | "What is the dosage for Lydrenex?" | Returns Zaloric (Veldra) dosage, not Aetheris |
| Fuzzy Matching / Typo | `clark-sentivue` | "Sentalink acceleration speed" | Corrects to Sentilink, returns result |
| Out of Scope | `quinn-aetheris` | "How do I make a chocolate cake?" | Guardrail message returned |

## AI Tools Used

### Tool

- **[Claude Code](https://docs.anthropic.com/en/docs/claude-code)** (Anthropic) - CLI-based AI coding assistant used throughout the project for architecture design, backend and frontend implementation, and debugging.

### How It Was Used

| Phase | What Claude Code Helped With |
|-------|------------------------------|
| **Architecture Design** | Designing the router/agentic pattern, deciding on separate ChromaDB collections for knowledge vs. submissions, and planning the multi-tenant data isolation strategy |
| **Backend Implementation** | Building the FastAPI search pipeline, ChromaDB ingestion with asset-type-aware chunking, intent classification prompts, and the three-tier guardrail system |
| **Frontend Development** | Scaffolding the Next.js app, building SSE stream parsing in the API client, and creating the component hierarchy (ThoughtTrace, CitationCard, RecommendationPanel) |
| **Debugging** | Fixing SSE streaming issues (frontend event parsing, connection handling) and tuning intent classification (queries being misrouted between KNOWLEDGE_SEARCH and GENERAL_PROFESSIONAL) |

### Key Prompts

Below are representative prompts that drove the core functionality:

1. **Initial scaffold**
   > "Read the BigSpring take-home PDF and build a FastAPI + Next.js search engine with ChromaDB for vector search, SQLite for relational data, and OpenAI for embeddings and generation."

2. **Intent classification tuning**
   > "The intent classifier is routing 'How do I handle price objections?' as KNOWLEDGE_SEARCH instead of GENERAL_PROFESSIONAL. Fix the system prompt to better distinguish between queries about assigned materials vs. general sales advice."

3. **SSE streaming fix**
   > "The frontend is not rendering streamed answer chunks - it accumulates them but only displays after the stream ends. Debug the SSE parsing in api.ts and fix the React state updates to render incrementally."

4. **Guardrails & data isolation**
   > "Ensure ChromaDB queries filter by the user's assigned play asset IDs before vector similarity search. Users should never see results from unassigned plays even within the same company."

5. **README generation**
   > "Read the take-home PDF and the full codebase, then create a README covering architecture, setup instructions, how it works, guardrails, and test cases."
