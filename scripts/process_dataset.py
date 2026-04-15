from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def process_dataset(input_path: Path, output_path: Path) -> None:
    if input_path.suffix == ".jsonl":
        df = pd.read_json(input_path, lines=True)
    elif input_path.suffix == ".csv":
        df = pd.read_csv(input_path)
    else:
        raise ValueError("Supported input formats are .jsonl and .csv")

    required = {"id", "question", "answer"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if "tags" not in df.columns:
        df["tags"] = [[] for _ in range(len(df))]

    df = df[["id", "question", "answer", "tags"]].dropna(subset=["id", "question", "answer"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    print(f"Processed {len(df)} records -> {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Normalize programming Q&A dataset")
    parser.add_argument("--input", required=True, help="Path to raw dataset (.jsonl or .csv)")
    parser.add_argument("--output", required=True, help="Path to output parquet file")

    args = parser.parse_args()
    process_dataset(Path(args.input), Path(args.output))
