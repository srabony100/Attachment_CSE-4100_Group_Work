# FAISS Index Pipeline

This step builds a reusable FAISS vector index from the processed JSON and fresh embeddings generated with GitHub Models.

## Inputs

- Processed records JSON: data/processed/stackoverflow_embedded_3000.json
- Embeddings matrix: data/index/stackoverflow_embeddings.npy

## What the script does

1. Loads processed records JSON.
2. Resolves embeddings .npy path from either:
   - --embeddings argument, or
   - each record embedding_ref.vector_store.
3. Validates record count equals vector count.
4. Optionally applies L2 normalization to vectors.
5. Builds FAISS IndexFlatIP and adds vectors.
6. Saves reusable backend startup artifacts:
   - question_index.faiss
   - id_map.npy
   - record_lookup.json

## Cosine similarity with FAISS

Cosine similarity between vectors a and b is:

cos(a, b) = (a · b) / (||a|| ||b||)

After L2 normalization, ||a|| = ||b|| = 1, so:

cos(a, b) = a · b

That allows cosine search to be implemented by:

- normalizing vectors,
- using FAISS inner-product index (IndexFlatIP).

## Backend files produced

- data/index/question_index.faiss
  - Reusable vector index loaded at backend startup.
- data/index/id_map.npy
  - Maps FAISS position to stable record_id.
- data/index/record_lookup.json
  - Metadata for result hydration (question, answer_snippet, tags, metadata, searchable_text).

## Command

Run from scripts folder:

python build_faiss_index_from_processed_json.py \
  --processed-json ../data/processed/stackoverflow_embedded_3000.json \
  --embeddings ../data/index/stackoverflow_embeddings.npy \
  --index-out ../data/index/question_index.faiss \
  --id-map-out ../data/index/id_map.npy \
  --lookup-out ../data/index/record_lookup.json \
  --normalize
