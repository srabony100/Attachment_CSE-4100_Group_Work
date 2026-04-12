# Deployment Guide (Free Tier)

## 1) Required Production Artifacts

Before deploying backend, ensure these files exist and are available to the service runtime:

- data/index/question_index.faiss
- data/index/id_map.npy
- data/index/record_lookup.json

These are produced by the Part 4 and Part 5 scripts.

## 2) Frontend on Vercel

### Project setup

1. Import repository in Vercel.
2. Set Root Directory to apps/web.
3. Vercel will detect Next.js automatically.

### Build and start

- Build command: npm run build
- Start command: npm run start

### Environment variables

- NEXT_PUBLIC_API_BASE_URL=https://your-backend-domain.onrender.com

Use apps/web/.env.production.example as reference.

## 3) Backend on Render

Use render.yaml in repository root.

### Build and start

- Build command: pip install -r requirements.txt
- Start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
- Root directory: apps/api

### Environment variables

Required:

- GITHUB_MODELS_API_KEY
- GITHUB_MODELS_ENDPOINT
- EMBEDDING_MODEL
- FAISS_INDEX_PATH
- ID_MAP_PATH
- LOOKUP_MAP_PATH
- CORS_ORIGINS

Recommended:

- EMBEDDING_TIMEOUT_SECONDS
- EMBEDDING_MAX_RETRIES
- EMBEDDING_BASE_BACKOFF_SECONDS
- DEFAULT_TOP_K

Use apps/api/.env.production.example as reference.

## 4) Backend on Railway

Use railway.json in repository root.

### Build and start

- Build command: cd apps/api && pip install -r requirements.txt
- Start command: cd apps/api && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

Set the same environment variables listed for Render.

## 5) FAISS and metadata storage strategy in deployment

Free-tier instances are commonly ephemeral. Use one of these patterns:

### Option A: Keep index artifacts in repository

Best for small index sizes.

- Commit question_index.faiss, id_map.npy, record_lookup.json under data/index.
- Configure paths:
  - FAISS_INDEX_PATH=../../data/index/question_index.faiss
  - ID_MAP_PATH=../../data/index/id_map.npy
  - LOOKUP_MAP_PATH=../../data/index/record_lookup.json

Pros: simplest startup and no download step.

Cons: repository size grows as index grows.

### Option B: Store artifacts in object storage and download at startup

Best when index files are too large for repository.

- Keep canonical artifacts in S3, R2, or similar.
- Download files to local runtime path (for example /tmp/data/index) before app starts.
- Point environment variables to downloaded local paths.

Pros: smaller repository and easier artifact rotation.

Cons: adds startup latency and requires download logic.

## 6) Frontend to backend production connectivity

To ensure frontend can call backend in production:

1. Set NEXT_PUBLIC_API_BASE_URL on Vercel to deployed backend URL.
2. Set backend CORS_ORIGINS to exact frontend origin.
3. Redeploy both services after env updates.
4. Verify with browser network tab that requests hit /search successfully.

## 7) Free-tier optimization notes

- Keep index size lean (use 3000-row index or compressed variant).
- Prefer lower top_k defaults to reduce response payload and latency.
- Keep embedding retries bounded (current defaults are suitable).
- Use exact CORS domains to avoid accidental preflight failures.
- Expect cold starts; surface user-friendly loading messages in frontend.

## 8) Deployment verification checklist

- /health returns status ok and index_loaded true.
- /search returns results for representative queries.
- Frontend loads and displays dynamic results from backend.
- Empty input is blocked with user guidance.
- Backend failure states render friendly messages.
- Result cards render score/tags and expandable details.

## 9) Quick validation queries

Run in app UI after deployment:

- how to declare array in python
- how to sort a list in javascript
- how to read file in c++

Expected: relevant top matches with meaningful titles/snippets and non-empty score values.
