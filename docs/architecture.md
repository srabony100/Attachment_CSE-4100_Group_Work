# Semantic Programming Search - Architecture Plan

## 1) Problem statement
Developers waste time searching exact keywords across large collections of programming Q&A data. Keyword search misses semantically similar questions with different wording, causing duplicate effort and slow debugging.

This product solves that by using vector embeddings for semantic retrieval, so users can ask natural language questions and get contextually similar programming answers quickly.

## 2) Target users
- Software engineers searching implementation help.
- Students learning algorithms, frameworks, and debugging patterns.
- Developer relations/support teams triaging technical issues.
- Technical content teams building "related questions" experiences.

## 3) Main features
- Natural language semantic search for programming questions.
- Top-k nearest-neighbor retrieval with similarity scores.
- Question + answer preview cards with metadata (tags, source, date).
- Filter and sort (tags, language, recency).
- Fast API endpoint for web and future clients.
- Rebuildable index pipeline from dataset files.
- Re-embedding pipeline with consistent model versioning.

## 4) User journey
1. User opens web app and types a programming question.
2. Frontend calls backend `/api/v1/search` with query and optional filters.
3. Backend generates query embedding using configured embedding model.
4. Backend searches FAISS index for nearest vectors.
5. Backend hydrates result metadata from structured store.
6. Backend returns ranked results and scores.
7. Frontend renders cards and allows refinement.

## 5) System architecture
- Frontend (Next.js): UI, input validation, rendering, loading/error states.
- API service (FastAPI): query embedding, vector retrieval, filtering, response shaping.
- Vector index (FAISS): in-memory/serialized ANN index for low-latency similarity search.
- Metadata store (Parquet/JSON/CSV initially; optionally DB later): question text, answers, tags.
- Offline scripts: dataset cleaning, chunking, embedding generation, FAISS build.

## 6) Tech stack
- Frontend: Next.js (App Router), TypeScript, Tailwind CSS.
- Backend: FastAPI, Pydantic, NumPy, FAISS.
- Data scripts: Python, pandas, NumPy, FAISS, requests/httpx.
- Optional model provider: GitHub Models embeddings endpoint.

## 7) Why vector search
Programming questions are often paraphrased. Vector search captures semantic meaning beyond exact token overlap.

Keyword query: "python list remove duplicates preserve order"

Semantically related result might contain: "deduplicate array while keeping insertion order".

BM25/LIKE may miss this; embeddings map both near each other in vector space.

## 8) Why FAISS instead of MySQL for semantic retrieval
- MySQL is optimized for relational/tabular operations, not high-dimensional nearest-neighbor search.
- FAISS is built for vector similarity and supports efficient ANN/flat indexes.
- Better latency and scalability for top-k vector queries.
- MySQL can still be used for metadata, but FAISS should power embedding similarity search.

## 9) Why fresh embeddings must use the same GitHub Models embedding model
The index vectors and query vectors must exist in the same embedding space.

If dataset vectors are generated with model A and queries with model B:
- vector dimensions may differ,
- geometric relationships differ,
- similarity rankings become unreliable.

Therefore, when updating data or reindexing, regenerate embeddings with the exact same model/version used for live query embeddings (for example, `text-embedding-3-large` configured through GitHub Models).

## 10) API overview
- `GET /health`: service readiness.
- `POST /api/v1/search`
  - Request:
    - `query: string`
    - `top_k: int (optional)`
    - `tags: string[] (optional)`
  - Response:
    - `query: string`
    - `results: [{id, question, answer_snippet, tags, score}]`

## 11) Data flow (dataset to frontend)
1. Raw dataset files saved in `data/raw`.
2. `scripts/process_dataset.py` normalizes fields into `data/processed/questions.parquet`.
3. `scripts/generate_embeddings.py` creates embeddings with configured GitHub Models embedding model.
4. Script persists:
   - `data/index/question_index.faiss`
   - `data/index/id_map.npy`
5. FastAPI loads FAISS index and metadata on startup.
6. Query from frontend -> embedding -> FAISS top-k IDs.
7. Backend joins IDs with metadata and returns ranked JSON.
8. Next.js renders results with score and filters.

## 12) Clean architecture summary
- Presentation layer: Next.js UI and API route client.
- Application layer: FastAPI search orchestration + request validation.
- Domain layer: semantic retrieval use cases and ranking contracts.
- Infrastructure layer: embedding provider client, FAISS index, file-based metadata.
- Data pipeline layer: ingestion, normalization, embedding generation, index build.
