from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Any

import numpy as np

try:
    import faiss  # pyright: ignore[reportMissingImports]
except ImportError:  # pragma: no cover - exercised only in environments without faiss
    faiss = None

from app.schemas.search import SearchResultItem
from app.services.local_embeddings import embed_texts
from app.services.embedder import Embedder


DEMO_RECORDS: list[dict[str, Any]] = [
    {
        "record_id": "react-useeffect-dev-double-run",
        "question": "Why does useEffect run twice in development?",
        "answer_snippet": "React Strict Mode intentionally double-invokes effects in development to catch side effects.",
        "tags": ["react", "useeffect", "strict-mode"],
    },
    {
        "record_id": "react-debounce-search-input",
        "question": "How can I debounce search input in React?",
        "answer_snippet": "Use useEffect with setTimeout and clearTimeout, or use lodash debounce with useMemo.",
        "tags": ["react", "debounce", "frontend"],
    },
    {
        "record_id": "fastapi-di-practices",
        "question": "FastAPI dependency injection best practices",
        "answer_snippet": "Keep dependencies small, typed, and composable via Depends for auth, DB sessions, and settings.",
        "tags": ["fastapi", "python", "dependency-injection"],
    },
    {
        "record_id": "sqlalchemy-n-plus-one",
        "question": "How do I avoid N+1 queries in SQLAlchemy?",
        "answer_snippet": "Use selectinload or joinedload for eager loading and inspect generated SQL in debug logs.",
        "tags": ["sqlalchemy", "python", "database"],
    },
    {
        "record_id": "pandas-groupby-optimize",
        "question": "How to optimize pandas groupby performance?",
        "answer_snippet": "Use categorical dtypes, avoid apply when possible, and aggregate with vectorized operations.",
        "tags": ["pandas", "python", "performance"],
    },
    {
        "record_id": "js-async-vs-defer",
        "question": "Difference between async and defer in JavaScript",
        "answer_snippet": "Async executes as soon as downloaded; defer preserves order and runs after HTML parsing.",
        "tags": ["javascript", "html", "web"],
    },
    {
        "record_id": "python-list-sort",
        "question": "How to sort a list in Python",
        "answer_snippet": "Use list.sort() in place or sorted(list_obj) to create a new sorted list.",
        "tags": ["python", "sorting"],
    },
    {
        "record_id": "js-array-sort",
        "question": "How to sort a list in JavaScript",
        "answer_snippet": "Use array.sort((a, b) => a - b) for numbers to avoid lexicographic sorting.",
        "tags": ["javascript", "sorting"],
    },
    {
        "record_id": "cpp-read-file",
        "question": "How to read a file in C++",
        "answer_snippet": "Use std::ifstream and std::getline to read file contents safely.",
        "tags": ["c++", "file-io"],
    },
]


class VectorStore:
    def __init__(self, index_path: str, id_map_path: str, lookup_map_path: str):
        self.index_path = Path(index_path)
        self.id_map_path = Path(id_map_path)
        self.lookup_map_path = Path(lookup_map_path)

        self.index: Any | None = None
        self.id_map = np.array([], dtype=object)
        self.lookup_by_id: dict[str, dict[str, Any]] = {}
        self.dimension: int = 0
        self._lock = Lock()

    @property
    def is_ready(self) -> bool:
        return self.index is not None and len(self.id_map) > 0 and len(self.lookup_by_id) > 0

    @staticmethod
    def _normalize_query(query_vector: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(query_vector)
        if norm == 0:
            return query_vector
        return query_vector / norm

    def ensure_demo_index(self) -> None:
        if self.index_path.exists() and self.id_map_path.exists() and self.lookup_map_path.exists():
            return

        if faiss is None:
            raise ImportError("faiss is required to build demo index")

        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.id_map_path.parent.mkdir(parents=True, exist_ok=True)
        self.lookup_map_path.parent.mkdir(parents=True, exist_ok=True)

        vectors = embed_texts(
            [
                f"{record['question']} {record['answer_snippet']} {' '.join(record['tags'])}"
                for record in DEMO_RECORDS
            ],
            dimension=1536,
        )

        index = faiss.IndexFlatIP(1536)
        index.add(vectors)
        faiss.write_index(index, str(self.index_path))

        id_map = np.array([record["record_id"] for record in DEMO_RECORDS], dtype=object)
        np.save(self.id_map_path, id_map)

        with self.lookup_map_path.open("w", encoding="utf-8") as fp:
            json.dump(DEMO_RECORDS, fp, ensure_ascii=True, indent=2)

    def rebuild_from_records(self, records: list[dict[str, Any]], embedder: Embedder) -> None:
        if faiss is None:
            raise ImportError("faiss is required to build vector index")
        if not records:
            raise ValueError("Cannot build an index with zero records")

        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.id_map_path.parent.mkdir(parents=True, exist_ok=True)
        self.lookup_map_path.parent.mkdir(parents=True, exist_ok=True)

        texts: list[str] = []
        for record in records:
            texts.append(
                f"{record.get('question', '')} {record.get('answer_snippet', '')} {' '.join(record.get('tags', []))}"
            )

        vectors = embedder.embed_batch(texts)
        if vectors.ndim != 2 or vectors.shape[0] != len(records):
            raise ValueError("Embedding count does not match record count")

        vectors = np.asarray(vectors, dtype=np.float32)
        index = faiss.IndexFlatIP(int(vectors.shape[1]))
        index.add(vectors)

        id_map = np.array([str(record.get("record_id")) for record in records], dtype=object)

        with self._lock:
            faiss.write_index(index, str(self.index_path))
            np.save(self.id_map_path, id_map)
            with self.lookup_map_path.open("w", encoding="utf-8") as fp:
                json.dump(records, fp, ensure_ascii=True, indent=2)
            self.load()

    def load(self) -> None:
        if faiss is None:
            raise ImportError("faiss is required to load the vector index")

        if not self.index_path.exists():
            raise FileNotFoundError(f"FAISS index not found: {self.index_path}")
        if not self.id_map_path.exists():
            raise FileNotFoundError(f"ID map not found: {self.id_map_path}")
        if not self.lookup_map_path.exists():
            raise FileNotFoundError(f"Lookup map not found: {self.lookup_map_path}")

        self.index = faiss.read_index(str(self.index_path))
        self.id_map = np.load(self.id_map_path, allow_pickle=True)
        self.dimension = int(self.index.d)

        with self.lookup_map_path.open("r", encoding="utf-8") as fp:
            lookup_records = json.load(fp)
        if not isinstance(lookup_records, list):
            raise ValueError("Lookup map must be a list of records")

        # Use an ID-keyed dictionary so FAISS hits can be hydrated in O(1).
        self.lookup_by_id = {
            str(record.get("record_id")): record
            for record in lookup_records
            if record.get("record_id") is not None
        }

        if len(self.id_map) != self.index.ntotal:
            raise ValueError(
                f"ID map count ({len(self.id_map)}) does not match index size ({self.index.ntotal})"
            )

    def search(self, query_vector: np.ndarray, top_k: int, tags: list[str]) -> list[SearchResultItem]:
        if not self.is_ready or self.index is None:
            return []

        if query_vector.shape[0] != self.dimension:
            raise ValueError(
                f"Query vector dimension mismatch. expected={self.dimension}, got={query_vector.shape[0]}"
            )

        query = np.array([self._normalize_query(query_vector)], dtype=np.float32)
        scores, idxs = self.index.search(query, top_k)

        results: list[SearchResultItem] = []
        for score, idx in zip(scores[0], idxs[0]):
            if idx < 0 or idx >= len(self.id_map):
                continue

            item_id = str(self.id_map[idx])
            record = self.lookup_by_id.get(item_id)
            if not record:
                continue

            record_tags = record.get("tags", []) or []
            normalized_tags = [str(tag).lower() for tag in record_tags]
            if tags and not set(tag.lower() for tag in tags).issubset(set(normalized_tags)):
                continue

            results.append(
                SearchResultItem(
                    record_id=item_id,
                    title=str(record.get("question", "")),
                    answer_snippet=str(record.get("answer_snippet", ""))[:300],
                    tags=record_tags,
                    similarity_score=float(score),
                )
            )

        return results
