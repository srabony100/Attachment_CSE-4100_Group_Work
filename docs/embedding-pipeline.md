# Fresh Embedding Pipeline (GitHub Models)

This pipeline generates fresh embeddings from the cleaned 3000-row JSON dataset.

## Goal

- Read clean JSON records from `data/raw/stackoverflow_clean_3000.json`
- Build one combined searchable field per record:
  - title + question body + answer + tags
- Call GitHub Models embeddings API
- Save vectors separately from records
- Save a processed JSON with embedding references

## Why one consistent model is mandatory

Cosine similarity only works correctly when both vectors were produced by the same embedding model and version.

If dataset vectors come from model A and query vectors come from model B:
- dimensions may differ,
- vector geometry differs,
- nearest-neighbor ranking becomes invalid or unstable.

Therefore, use one model id for:
- indexing dataset rows now,
- embedding user queries at search time later.

## Files produced

- Embeddings matrix: `data/index/stackoverflow_embeddings.npy`
- Processed records JSON: `data/processed/stackoverflow_embedded_3000.json`
- Manifest JSON: `data/index/embedding_manifest.json`

## Processed JSON format

```json
{
  "record_id": "12345",
  "question": {
    "title": "...",
    "body": "..."
  },
  "answer": {
    "text": "..."
  },
  "tags": ["python", "pandas"],
  "metadata": {
    "score": 11,
    "source_row_index": 77
  },
  "searchable_text": "Title: ...\nQuestion: ...\nAnswer: ...\nTags: python, pandas",
  "embedding_ref": {
    "index": 0,
    "model": "text-embedding-3-large",
    "dimension": 1536,
    "vector_store": "../data/index/stackoverflow_embeddings.npy"
  }
}
```

## Command

```bash
cd scripts
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GITHUB_MODELS_API_KEY="your_token"
export EMBEDDING_MODEL="text-embedding-3-large"
python generate_fresh_embeddings_github_models.py \
  --input ../data/raw/stackoverflow_clean_3000.json \
  --output-records ../data/processed/stackoverflow_embedded_3000.json \
  --output-embeddings ../data/index/stackoverflow_embeddings.npy
```

## Retry and failure handling

- Retries transient failures (`429`, `5xx`, network errors)
- Exponential backoff with jitter
- Batch progress logs via `tqdm` and per-batch counters
