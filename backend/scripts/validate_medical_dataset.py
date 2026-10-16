"""Validate the structure and basic consistency of the MediBot medical dataset."""

import json
import re
import sys
from pathlib import Path


REQUIRED_FIELDS = {
    "id", "question", "answer", "keywords", "category", "severity", "related_questions"
}
NEW_RECORD_FIELDS = {"source_name", "source_url", "reviewed_at", "language"}


def normalize(text):
    return re.sub(r"[^a-z0-9]+", " ", text.casefold()).strip()


def validate(path):
    records = json.loads(path.read_text(encoding="utf-8"))
    errors = []
    if not isinstance(records, list):
        raise ValueError("Dataset root must be a JSON array")
    ids = [item.get("id") for item in records if isinstance(item, dict)]
    if not records:
        errors.append("Dataset is empty")
    if len(ids) != len(set(ids)):
        errors.append("Record IDs are not unique")
    if set(ids) != set(range(len(records))):
        errors.append(f"IDs must be contiguous integers from 0 through {len(records) - 1}")
    questions = {}
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"Record {index} is not an object")
            continue
        missing = REQUIRED_FIELDS - record.keys()
        if missing:
            errors.append(f"Record {index} missing fields: {', '.join(sorted(missing))}")
        missing_meta = NEW_RECORD_FIELDS - record.keys()
        if missing_meta:
            errors.append(f"Record {index} missing metadata: {', '.join(sorted(missing_meta))}")
        if record.get("reviewed_at") is not None:
            errors.append(f"Record {index}: reviewed_at must remain null")
        source_url = record.get("source_url")
        if not isinstance(source_url, str) or not source_url.startswith("https://"):
            errors.append(f"Record {index}: source_url must be an HTTPS URL")
        question = normalize(str(record.get("question", "")))
        if question in questions:
            errors.append(f"Duplicate question at IDs {questions[question]} and {record.get('id')}: {question}")
        questions[question] = record.get("id")
        if not isinstance(record.get("keywords"), list) or not isinstance(record.get("related_questions"), list):
            errors.append(f"Record {index}: keywords and related_questions must be arrays")
    return records, errors


if __name__ == "__main__":
    dataset = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parents[1] / "data" / "data_enriched_v3.json"
    try:
        data, problems = validate(dataset)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"INVALID: {exc}")
        raise SystemExit(1)
    counts = {}
    for item in data:
        counts[item.get("category", "<missing>")] = counts.get(item.get("category", "<missing>"), 0) + 1
    print(f"Records: {len(data)}; unique IDs: {len({item.get('id') for item in data})}")
    print("By category: " + ", ".join(f"{key}={value}" for key, value in sorted(counts.items())))
    if problems:
        print("INVALID")
        for problem in problems:
            print(f"- {problem}")
        raise SystemExit(1)
    print("VALID")
