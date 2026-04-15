from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import faiss
import numpy as np


def l2_normalize(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    return vectors / norms


def load_processed_records(processed_json_path: Path) -> list[dict[str, Any]]:
    if not processed_json_path.exists():
        raise FileNotFoundError(f"Processed JSON not found: {processed_json_path}")

    with processed_json_path.open("r", encoding="utf-8") as fp:
        records = json.load(fp)

    if not isinstance(records, list):
        raise ValueError("Processed JSON must be a list of records")

    return records


def resolve_embeddings_path(records: list[dict[str, Any]], processed_json_path: Path, cli_path: str | None) -> Path:
    if cli_path:
        path = Path(cli_path)
        return path if path.is_absolute() else (Path.cwd() / path).resolve()

    for record in records:
        embedding_ref = record.get("embedding_ref") or {}
        vector_store = embedding_ref.get("vector_store")
        if not vector_store:
            continue

        candidate = Path(vector_store)
        if candidate.is_absolute():
            return candidate

        # Resolve relative paths from the processed JSON file location.
        return (processed_json_path.parent / candidate).resolve()

    raise ValueError(
        "Could not resolve embeddings path. Provide --embeddings or include embedding_ref.vector_store in records."
    )


def build_lookup_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lookup: list[dict[str, Any]] = []
    for idx, record in enumerate(records):
        question = record.get("question") or {}
        answer = record.get("answer") or {}

        lookup.append(
            {
                "index": idx,
                "record_id": str(record.get("record_id", f"row-{idx}")),
                "question": str(question.get("title") or question.get("body") or ""),
                "answer_snippet": str(answer.get("text") or "")[:300],
                "tags": record.get("tags", []) or [],
                "metadata": record.get("metadata", {}) or {},
                "searchable_text": record.get("searchable_text", "") or "",
            }
        )
    return lookup


def build_faiss_index(
    processed_json_path: Path,
    index_out_path: Path,
    id_map_out_path: Path,
    lookup_out_path: Path,
    normalize_for_cosine: bool,
    embeddings_path: str | None,
) -> None:
    records = load_processed_records(processed_json_path)
    print(f"Loaded {len(records)} processed records from {processed_json_path}")

    vectors_path = resolve_embeddings_path(records, processed_json_path, embeddings_path)
    if not vectors_path.exists():
        raise FileNotFoundError(f"Embeddings .npy file not found: {vectors_path}")

    vectors = np.load(vectors_path)
    if vectors.ndim != 2:
        raise ValueError(f"Expected a 2D embedding matrix, got shape={vectors.shape}")

    if len(records) != vectors.shape[0]:
        raise ValueError(
            f"Record/vector count mismatch: records={len(records)} vectors={vectors.shape[0]}"
        )

    vectors = vectors.astype(np.float32)
    if normalize_for_cosine:
        print("Applying L2 normalization so inner product equals cosine similarity")
        vectors = l2_normalize(vectors)

    dimension = int(vectors.shape[1])
    index = faiss.IndexFlatIP(dimension)
    index.add(vectors)

    index_out_path.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(index_out_path))

    id_map = np.array([str(record.get("record_id", f"row-{idx}")) for idx, record in enumerate(records)], dtype=object)
    id_map_out_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(id_map_out_path, id_map)

    lookup_records = build_lookup_records(records)
    lookup_out_path.parent.mkdir(parents=True, exist_ok=True)
    with lookup_out_path.open("w", encoding="utf-8") as fp:
        json.dump(lookup_records, fp, ensure_ascii=False, indent=2)

    print(f"FAISS index written to: {index_out_path}")
    print(f"ID map written to: {id_map_out_path}")
    print(f"Lookup metadata written to: {lookup_out_path}")
    print(f"Index type: IndexFlatIP | dimension={dimension} | vectors={vectors.shape[0]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build FAISS index from processed JSON and embeddings produced by the GitHub Models pipeline."
    )
    parser.add_argument(
        "--processed-json",
        default="../data/processed/stackoverflow_embedded_3000.json",
        help="Path to processed JSON from generate_fresh_embeddings_github_models.py",
    )
    parser.add_argument(
        "--embeddings",
        default="",
        help="Optional path to embeddings .npy. If omitted, uses embedding_ref.vector_store from processed JSON.",
    )
    parser.add_argument(
        "--index-out",
        default="../data/index/question_index.faiss",
        help="Output path for FAISS index",
    )
    parser.add_argument(
        "--id-map-out",
        default="../data/index/id_map.npy",
        help="Output path for ID map (vector index -> record_id)",
    )
    parser.add_argument(
        "--lookup-out",
        default="../data/index/record_lookup.json",
        help="Output path for lookup metadata used by backend result hydration",
    )
    parser.add_argument(
        "--normalize",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="L2 normalize vectors before indexing (recommended for cosine similarity)",
    )

    args = parser.parse_args()
    build_faiss_index(
        processed_json_path=Path(args.processed_json),
        index_out_path=Path(args.index_out),
        id_map_out_path=Path(args.id_map_out),
        lookup_out_path=Path(args.lookup_out),
        normalize_for_cosine=bool(args.normalize),
        embeddings_path=args.embeddings or None,
    )
