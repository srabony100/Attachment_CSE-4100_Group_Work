# Dataset JSON Schema

This project exports a cleaned JSON file from:

- `MartinElMolon/stackoverflow_preguntas_con_embeddings`

Embeddings in the source are intentionally ignored at this stage.

## Export file

- Default output: `data/raw/stackoverflow_clean_3000.json`
- Format: JSON array of records
- Target size: 3000 cleaned records

## Canonical record schema

```json
{
  "record_id": "string",
  "question": {
    "title": "string",
    "body": "string"
  },
  "answer": {
    "text": "string"
  },
  "tags": ["string"],
  "metadata": {
    "score": "number (optional)",
    "creation_date": "string (optional)",
    "view_count": "number (optional)",
    "answer_count": "number (optional)",
    "source": "string (optional)",
    "language": "string (optional)",
    "source_row_index": "number"
  }
}
```

## Field selection policy

The export script inspects all available dataset columns and maps them to canonical fields using known aliases:

- `record_id`: from `id`, `question_id`, `qid`, or fallback to `row-{index}`
- `question.title`: from fields like `question_title`, `title`, `pregunta_titulo`
- `question.body`: from fields like `question_body`, `body`, `question_text`, `pregunta_cuerpo`, `question`
- `answer.text`: from fields like `answer`, `accepted_answer`, `best_answer`, `respuesta`
- `tags`: from `tags`, `tag`, `question_tags`, `etiquetas`
- `metadata`: best-effort from score/date/views/count/source/language columns when present

## Null cleaning rules

- Records without answer text are dropped.
- Records without both title and body are dropped.
- String nulls become empty strings.
- Missing tags become `[]`.
- Empty metadata keys are removed.

## Example record

```json
{
  "record_id": "12345",
  "question": {
    "title": "How can I remove duplicates from a Python list preserving order?",
    "body": "I have a list with repeated values and need to keep insertion order. What is the best approach?"
  },
  "answer": {
    "text": "Use dict.fromkeys(list_values) in Python 3.7+ to preserve insertion order, then cast back to list."
  },
  "tags": ["python", "list", "duplicates"],
  "metadata": {
    "score": 17,
    "creation_date": "2020-02-10T13:43:00Z",
    "view_count": 4200,
    "answer_count": 3,
    "language": "es",
    "source_row_index": 8821
  }
}
```

## Run command

```bash
cd scripts
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python export_hf_dataset_to_json.py --rows 3000 --output ../data/raw/stackoverflow_clean_3000.json
```
