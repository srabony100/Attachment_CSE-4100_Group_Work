from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import faiss
import numpy as np
import pandas as pd


def embed_text(text: str, model_name: str, dimension: int) -> np.ndarray:
    # Deterministic placeholder vector; replace with GitHub Models embeddings API.
    digest = hashlib.sha256(f"{model_name}:{text}".encode("utf-8")).digest()
    seed = int.from_bytes(digest[:8], "big", signed=False)
    rng = np.random.default_rng(seed)
    vector = rng.standard_normal(dimension).astype(np.float32)
    norm = np.linalg.norm(vector)
    return vector if norm == 0 else vector / norm


def generate_index(input_path: Path, index_out: Path, map_out: Path, model_name: str, dimension: int) -> None:
    df = pd.read_parquet(input_path)
    if any(column not in df.columns for column in ["id", "question"]):
        raise ValueError("Input parquet must include 'id' and 'question' columns")

    vectors = np.vstack([embed_text(text, model_name, dimension) for text in df["question"].astype(str)]).astype(
        np.float32
    )

    index = faiss.IndexFlatIP(dimension)
    index.add(vectors)

    index_out.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(index_out))

    id_map = df["id"].astype(str).to_numpy()
    np.save(map_out, id_map)

    print(f"Wrote FAISS index: {index_out}")
    print(f"Wrote ID map: {map_out}")
    print(f"Records indexed: {len(df)}")
    print(f"Embedding model used: {model_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate embeddings and FAISS index")
    parser.add_argument("--input", required=True, help="Path to processed parquet")
    parser.add_argument("--index-out", required=True, help="Path to .faiss output")
    parser.add_argument("--map-out", required=True, help="Path to .npy id map output")
    parser.add_argument("--model", default="text-embedding-3-large", help="Embedding model identifier")
    parser.add_argument("--dimension", type=int, default=1536, help="Embedding vector dimension")

    args = parser.parse_args()
    generate_index(
        input_path=Path(args.input),
        index_out=Path(args.index_out),
        map_out=Path(args.map_out),
        model_name=args.model,
        dimension=args.dimension,
    )
