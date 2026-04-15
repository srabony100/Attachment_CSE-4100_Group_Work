from __future__ import annotations

import argparse
import json
import os
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
import numpy as np
from tqdm import tqdm


RETRIABLE_STATUS_CODES = {408, 409, 425, 429, 500, 502, 503, 504}


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_tags(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [normalize_text(tag) for tag in value if normalize_text(tag)]

    raw = normalize_text(value)
    if not raw:
        return []

    for separator in [",", "|", ";"]:
        if separator in raw:
            return [item.strip() for item in raw.split(separator) if item.strip()]

    return [raw]


def build_searchable_text(record: dict[str, Any]) -> str:
    question = record.get("question", {}) or {}
    answer = record.get("answer", {}) or {}

    title = normalize_text(question.get("title"))
    body = normalize_text(question.get("body"))
    answer_text = normalize_text(answer.get("text"))
    tags = normalize_tags(record.get("tags"))

    parts = [
        f"Title: {title}" if title else "",
        f"Question: {body}" if body else "",
        f"Answer: {answer_text}" if answer_text else "",
        f"Tags: {', '.join(tags)}" if tags else "",
    ]

    combined = "\n".join(part for part in parts if part).strip()
    return combined


def chunked(items: list[Any], size: int) -> list[list[Any]]:
    return [items[idx : idx + size] for idx in range(0, len(items), size)]


@dataclass
class GitHubModelsEmbedder:
    endpoint: str
    api_key: str
    model: str
    timeout_seconds: float
    max_retries: int
    base_backoff_seconds: float

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        payload = {
            "input": texts,
            "model": self.model,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        for attempt in range(self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout_seconds) as client:
                    response = client.post(self.endpoint, headers=headers, json=payload)
                response.raise_for_status()
                body = response.json()
                return self._extract_embeddings(body)
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                should_retry = status in RETRIABLE_STATUS_CODES and attempt < self.max_retries
                if not should_retry:
                    raise
                delay = self._retry_delay(attempt)
                print(f"Retrying after HTTP {status}. attempt={attempt + 1}/{self.max_retries}, sleep={delay:.2f}s")
                time.sleep(delay)
            except httpx.RequestError as exc:
                should_retry = attempt < self.max_retries
                if not should_retry:
                    raise RuntimeError(f"Request failed after retries: {exc}") from exc
                delay = self._retry_delay(attempt)
                print(f"Retrying after network error. attempt={attempt + 1}/{self.max_retries}, sleep={delay:.2f}s")
                time.sleep(delay)

        raise RuntimeError("Embedding request failed after all retries")

    def _retry_delay(self, attempt: int) -> float:
        jitter = random.uniform(0, 0.25)
        return self.base_backoff_seconds * (2**attempt) + jitter

    @staticmethod
    def _extract_embeddings(body: dict[str, Any]) -> list[list[float]]:
        if "data" in body and isinstance(body["data"], list):
            return [item["embedding"] for item in body["data"] if "embedding" in item]

        if "embeddings" in body and isinstance(body["embeddings"], list):
            return body["embeddings"]

        raise ValueError(f"Unexpected embeddings response format: keys={list(body.keys())}")


def run_pipeline(
    input_path: Path,
    output_records_path: Path,
    output_embeddings_path: Path,
    output_manifest_path: Path,
    endpoint: str,
    api_key: str,
    model: str,
    batch_size: int,
    timeout_seconds: float,
    max_retries: int,
    base_backoff_seconds: float,
) -> None:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with input_path.open("r", encoding="utf-8") as fp:
        records = json.load(fp)

    if not isinstance(records, list):
        raise ValueError("Input JSON must be an array of records")

    print(f"Loaded {len(records)} records from {input_path}")

    prepared_records: list[dict[str, Any]] = []
    searchable_texts: list[str] = []

    for idx, record in enumerate(records):
        searchable_text = build_searchable_text(record)
        if not searchable_text:
            continue

        prepared_records.append(record)
        searchable_texts.append(searchable_text)

    print(f"Prepared {len(prepared_records)} records with searchable text")

    if not searchable_texts:
        raise ValueError("No valid searchable records found")

    embedder = GitHubModelsEmbedder(
        endpoint=endpoint,
        api_key=api_key,
        model=model,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        base_backoff_seconds=base_backoff_seconds,
    )

    all_embeddings: list[list[float]] = []
    batches = chunked(searchable_texts, batch_size)

    print(
        "Embedding records using one consistent model for index-time and query-time vectors: "
        f"{model}"
    )

    for batch_idx, batch_texts in enumerate(tqdm(batches, desc="Embedding batches", unit="batch"), start=1):
        vectors = embedder.embed_batch(batch_texts)
        if len(vectors) != len(batch_texts):
            raise ValueError(
                f"Embedding count mismatch in batch {batch_idx}: got {len(vectors)}, expected {len(batch_texts)}"
            )
        all_embeddings.extend(vectors)
        print(f"Batch {batch_idx}/{len(batches)} complete; total embedded={len(all_embeddings)}")

    embedding_matrix = np.array(all_embeddings, dtype=np.float32)
    dimension = int(embedding_matrix.shape[1])

    output_embeddings_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(output_embeddings_path, embedding_matrix)

    processed_records: list[dict[str, Any]] = []
    for idx, (record, searchable_text) in enumerate(zip(prepared_records, searchable_texts)):
        processed_records.append(
            {
                "record_id": normalize_text(record.get("record_id")) or f"row-{idx}",
                "question": record.get("question", {}),
                "answer": record.get("answer", {}),
                "tags": normalize_tags(record.get("tags")),
                "metadata": record.get("metadata", {}),
                "searchable_text": searchable_text,
                "embedding_ref": {
                    "index": idx,
                    "model": model,
                    "dimension": dimension,
                    "vector_store": str(output_embeddings_path),
                },
            }
        )

    output_records_path.parent.mkdir(parents=True, exist_ok=True)
    with output_records_path.open("w", encoding="utf-8") as fp:
        json.dump(processed_records, fp, ensure_ascii=False, indent=2)

    manifest = {
        "model": model,
        "endpoint": endpoint,
        "records_embedded": len(processed_records),
        "embedding_dimension": dimension,
        "embeddings_file": str(output_embeddings_path),
        "processed_records_file": str(output_records_path),
        "notes": "Use the same model for future query embeddings to keep vectors in one semantic space.",
    }

    output_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with output_manifest_path.open("w", encoding="utf-8") as fp:
        json.dump(manifest, fp, ensure_ascii=False, indent=2)

    print(f"Saved embedding matrix -> {output_embeddings_path}")
    print(f"Saved processed records -> {output_records_path}")
    print(f"Saved pipeline manifest -> {output_manifest_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate fresh embeddings from clean JSON using GitHub Models."
    )
    parser.add_argument(
        "--input",
        default="../data/raw/stackoverflow_clean_3000.json",
        help="Input JSON dataset path",
    )
    parser.add_argument(
        "--output-records",
        default="../data/processed/stackoverflow_embedded_3000.json",
        help="Output JSON with searchable_text + embedding references",
    )
    parser.add_argument(
        "--output-embeddings",
        default="../data/index/stackoverflow_embeddings.npy",
        help="Output .npy file containing embedding vectors",
    )
    parser.add_argument(
        "--output-manifest",
        default="../data/index/embedding_manifest.json",
        help="Output JSON with pipeline metadata",
    )
    parser.add_argument(
        "--endpoint",
        default=os.getenv("GITHUB_MODELS_ENDPOINT", "https://models.inference.ai.azure.com/embeddings"),
        help="GitHub Models embeddings endpoint",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("GITHUB_MODELS_API_KEY", ""),
        help="GitHub Models API key (or set GITHUB_MODELS_API_KEY env var)",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("EMBEDDING_MODEL", "text-embedding-3-large"),
        help="Embedding model id (must be reused for query embeddings)",
    )
    parser.add_argument("--batch-size", type=int, default=20, help="Records per request")
    parser.add_argument("--timeout", type=float, default=45.0, help="HTTP timeout in seconds")
    parser.add_argument("--max-retries", type=int, default=5, help="Max retries for transient API failures")
    parser.add_argument(
        "--base-backoff",
        type=float,
        default=1.0,
        help="Base retry backoff in seconds (exponential + jitter)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if not args.api_key:
        raise ValueError("Missing API key. Set --api-key or GITHUB_MODELS_API_KEY environment variable.")

    run_pipeline(
        input_path=Path(args.input),
        output_records_path=Path(args.output_records),
        output_embeddings_path=Path(args.output_embeddings),
        output_manifest_path=Path(args.output_manifest),
        endpoint=args.endpoint,
        api_key=args.api_key,
        model=args.model,
        batch_size=args.batch_size,
        timeout_seconds=args.timeout,
        max_retries=args.max_retries,
        base_backoff_seconds=args.base_backoff,
    )
