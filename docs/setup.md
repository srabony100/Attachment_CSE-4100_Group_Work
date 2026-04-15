# Setup Notes

## Install commands

### 1) Frontend
```bash
cd apps/web
npm install
npm run dev
```

### 2) Backend
```bash
cd apps/api
python3 -m venv .venv
.venv/bin/python -m pip install -U pip
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --port 8000
```

### 3) Scripts
```bash
cd scripts
python3 -m venv .venv
.venv/bin/python -m pip install -U pip
.venv/bin/pip install -r requirements.txt
python process_dataset.py --input ../data/raw/questions.jsonl --output ../data/processed/questions.parquet
python generate_embeddings.py --input ../data/processed/questions.parquet --index-out ../data/index/question_index.faiss --map-out ../data/index/id_map.npy
```

### 4) Dataset export from Hugging Face
```bash
cd scripts
python3 -m venv .venv
.venv/bin/python -m pip install -U pip
.venv/bin/pip install -r requirements.txt
python export_hf_dataset_to_json.py --rows 3000 --output ../data/raw/stackoverflow_clean_3000.json
```

### 5) Fresh embeddings via GitHub Models
```bash
cd scripts
python3 -m venv .venv
.venv/bin/python -m pip install -U pip
.venv/bin/pip install -r requirements.txt
export GITHUB_MODELS_API_KEY="your_token"
export EMBEDDING_MODEL="text-embedding-3-large"
python generate_fresh_embeddings_github_models.py \
	--input ../data/raw/stackoverflow_clean_3000.json \
	--output-records ../data/processed/stackoverflow_embedded_3000.json \
	--output-embeddings ../data/index/stackoverflow_embeddings.npy
```

### 6) Build FAISS index from fresh embeddings
```bash
cd scripts
python3 -m venv .venv
.venv/bin/python -m pip install -U pip
.venv/bin/pip install -r requirements.txt
python build_faiss_index_from_processed_json.py \
	--processed-json ../data/processed/stackoverflow_embedded_3000.json \
	--embeddings ../data/index/stackoverflow_embeddings.npy \
	--index-out ../data/index/question_index.faiss \
	--id-map-out ../data/index/id_map.npy \
	--lookup-out ../data/index/record_lookup.json \
	--normalize
```

## Environment variable plan

### Root (`.env`)
- `EMBEDDING_MODEL`: canonical embedding model id.
- `TOP_K`: default top-k for search.

### Frontend (`apps/web/.env.local`)
- `NEXT_PUBLIC_API_BASE_URL`: backend base URL, e.g. `http://localhost:8000`.

### Backend (`apps/api/.env`)
- `API_TITLE`: FastAPI service title.
- `API_VERSION`: API version string.
- `GITHUB_MODELS_API_KEY`: token for embeddings API.
- `GITHUB_MODELS_ENDPOINT`: endpoint for embeddings model.
- `EMBEDDING_MODEL`: must match indexing model.
- `FAISS_INDEX_PATH`: path to `.faiss` file.
- `ID_MAP_PATH`: path to id map `.npy` file.
- `METADATA_PATH`: path to processed metadata.
- `DEFAULT_TOP_K`: fallback number of results.

### Scripts environment
- `GITHUB_MODELS_API_KEY`: token used by embedding pipeline script.
- `GITHUB_MODELS_ENDPOINT`: embeddings endpoint (default is GitHub Models endpoint).
- `EMBEDDING_MODEL`: must match model used by backend query embeddings.

## Naming conventions
- Folders: `kebab-case` or domain grouping (`apps/api/app/services`).
- Python modules: `snake_case.py`.
- TypeScript files: `kebab-case` for route-level files, `PascalCase` for component names if components are added.
- API path prefix: `/api/v1`.
- Dataset columns: `id`, `question`, `answer`, `tags`.
