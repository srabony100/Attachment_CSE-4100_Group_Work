# FastAPI Semantic Search API

## API structure

- App entrypoint: apps/api/app/main.py
- Routes: apps/api/app/api/routes/search.py
- Schemas: apps/api/app/schemas/search.py
- Embedding service: apps/api/app/services/embedder.py
- Vector search service: apps/api/app/services/vector_store.py
- Settings: apps/api/app/core/config.py

## Endpoints

### GET /health

Health and readiness check.

Response:

```json
{
  "status": "ok",
  "index_loaded": true,
  "index_size": 3000,
  "embedding_model": "text-embedding-3-large"
}
```

### POST /search

Semantic search endpoint.

Alias also available:

- POST /api/v1/search

Request body:

```json
{
  "query": "How do I avoid N+1 queries in SQLAlchemy?",
  "top_k": 10,
  "tags": ["python", "sqlalchemy"]
}
```

Response body:

```json
{
  "query": "How do I avoid N+1 queries in SQLAlchemy?",
  "results": [
    {
      "record_id": "14829",
      "title": "SQLAlchemy eager loading best practices",
      "answer_snippet": "Use selectinload or joinedload depending on cardinality...",
      "tags": ["python", "sqlalchemy", "orm"],
      "similarity_score": 0.8732
    }
  ]
}
```

## Error handling

- 422 validation errors are returned in structured JSON.
- 503 when search service is not ready.
- 400 for client-side query/vector issues.
- 502 for upstream embedding failures.
- 500 fallback for unhandled server errors.

## CORS

CORS middleware is enabled with origins from:

- CORS_ORIGINS in apps/api/.env

Example:

- CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

## Startup behavior

On startup, the app loads:

- FAISS index file
- ID map file
- Lookup metadata file

This makes semantic search reusable and fast for all requests without per-request disk loading.
