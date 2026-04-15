from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

from datasets import load_dataset


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_tags(value: Any) -> list[str]:
    if value is None:
        return []

    if isinstance(value, list):
        tags = [normalize_text(tag) for tag in value]
        return [tag for tag in tags if tag]

    text = normalize_text(value)
    if not text:
        return []

    separators = [",", "|", ";"]
    for sep in separators:
        if sep in text:
            return [part.strip() for part in text.split(sep) if part.strip()]

    return [text]


def pick_column(columns: list[str], candidates: list[str]) -> str | None:
    lowered = {column.lower(): column for column in columns}

    for candidate in candidates:
        if candidate.lower() in lowered:
            return lowered[candidate.lower()]

    for candidate in candidates:
        for column in columns:
            if candidate.lower() in column.lower():
                return column

    return None


def build_field_map(columns: list[str]) -> dict[str, str | None]:
    return {
        "id": pick_column(columns, ["id", "question_id", "qid", "stack_id"]),
        "title": pick_column(
            columns,
            [
                "question_title",
                "title",
                "pregunta_titulo",
                "titulo",
            ],
        ),
        "body": pick_column(
            columns,
            [
                "question_body",
                "body",
                "question_text",
                "pregunta_cuerpo",
                "cuerpo",
                "question",
            ],
        ),
        "answer": pick_column(
            columns,
            [
                "answer",
                "accepted_answer",
                "best_answer",
                "answer_body",
                "respuesta",
            ],
        ),
        "tags": pick_column(columns, ["tags", "tag", "question_tags", "etiquetas"]),
        "score": pick_column(columns, ["score", "question_score"]),
        "creation_date": pick_column(columns, ["creation_date", "created_at", "date", "fecha"]),
        "view_count": pick_column(columns, ["view_count", "views"]),
        "answer_count": pick_column(columns, ["answer_count"]),
        "source": pick_column(columns, ["source", "dataset", "origin"]),
        "lang": pick_column(columns, ["lang", "language", "idioma"]),
    }


def clean_metadata(record: dict[str, Any]) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    for key, value in record.items():
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        metadata[key] = value
    return metadata


def build_record(
    row: dict[str, Any],
    field_map: dict[str, str | None],
    row_index: int,
) -> dict[str, Any]:
    raw_id = row.get(field_map["id"]) if field_map["id"] else None
    raw_title = row.get(field_map["title"]) if field_map["title"] else None
    raw_body = row.get(field_map["body"]) if field_map["body"] else None
    raw_answer = row.get(field_map["answer"]) if field_map["answer"] else None
    raw_tags = row.get(field_map["tags"]) if field_map["tags"] else None

    title = normalize_text(raw_title)
    body = normalize_text(raw_body)
    answer = normalize_text(raw_answer)
    tags = normalize_tags(raw_tags)

    if not answer:
        return {}
    if not title and not body:
        return {}

    record_id = normalize_text(raw_id) or f"row-{row_index}"

    metadata_fields = {
        "score": row.get(field_map["score"]) if field_map["score"] else None,
        "creation_date": normalize_text(row.get(field_map["creation_date"])) if field_map["creation_date"] else "",
        "view_count": row.get(field_map["view_count"]) if field_map["view_count"] else None,
        "answer_count": row.get(field_map["answer_count"]) if field_map["answer_count"] else None,
        "source": normalize_text(row.get(field_map["source"])) if field_map["source"] else "",
        "language": normalize_text(row.get(field_map["lang"])) if field_map["lang"] else "",
        "source_row_index": row_index,
    }

    return {
        "record_id": record_id,
        "question": {
            "title": title,
            "body": body,
        },
        "answer": {
            "text": answer,
        },
        "tags": tags,
        "metadata": clean_metadata(metadata_fields),
    }


def export_dataset(
    dataset_name: str,
    split_name: str,
    output_path: Path,
    target_rows: int,
    seed: int,
) -> None:
    print(f"Loading dataset: {dataset_name} (split={split_name})")
    dataset = load_dataset(dataset_name, split=split_name)

    columns = list(dataset.column_names)
    print("Available columns:")
    for column in columns:
        print(f"- {column}")

    field_map = build_field_map(columns)
    print("\nSelected column mapping:")
    for key, value in field_map.items():
        print(f"- {key}: {value}")

    indices = list(range(len(dataset)))
    rng = random.Random(seed)
    rng.shuffle(indices)

    selected: list[dict[str, Any]] = []
    for row_index in indices:
        row = dataset[row_index]
        record = build_record(row=row, field_map=field_map, row_index=row_index)
        if not record:
            continue

        selected.append(record)
        if len(selected) >= target_rows:
            break

    if len(selected) < target_rows:
        print(
            f"Warning: only {len(selected)} valid rows were found after cleaning; requested {target_rows}."
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fp:
        json.dump(selected, fp, ensure_ascii=False, indent=2)

    print(f"\nSaved {len(selected)} cleaned records -> {output_path}")
    print("Nulls are removed by using empty strings/lists and pruning empty metadata keys.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download MartinElMolon/stackoverflow_preguntas_con_embeddings and export clean JSON."
    )
    parser.add_argument(
        "--dataset",
        default="MartinElMolon/stackoverflow_preguntas_con_embeddings",
        help="Hugging Face dataset name",
    )
    parser.add_argument("--split", default="train", help="Dataset split to read")
    parser.add_argument(
        "--output",
        default="../data/raw/stackoverflow_clean_3000.json",
        help="Output JSON path",
    )
    parser.add_argument("--rows", type=int, default=3000, help="Number of cleaned rows to export")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for row sampling")

    args = parser.parse_args()
    export_dataset(
        dataset_name=args.dataset,
        split_name=args.split,
        output_path=Path(args.output),
        target_rows=args.rows,
        seed=args.seed,
    )
