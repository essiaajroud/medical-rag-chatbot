
#!/usr/bin/env python3
"""
Validate a medical JSON dataset.

Usage from the project root:

    python backend/scripts/validate_medical_dataset.py \
        backend/data/data_enriched_v3_reviewed_copy.json \
        backend/data/data_enriched.json

The original records may use the legacy schema.
New records must include source metadata.
"""

import json
import re
import sys
from pathlib import Path
from collections import Counter


# Existing fields required by the RAG application.
REQUIRED_FIELDS = {
    "id",
    "question",
    "answer",
    "keywords",
    "category",
    "severity",
    "related_questions",
}

# Metadata required for new records.
METADATA_FIELDS = {
    "source_name",
    "source_url",
    "reviewed_at",
    "language",
}

VALID_SEVERITIES = {
    "low",
    "medium",
    "high",
    "critical",
}

URL_PATTERN = re.compile(r"^https?://\S+$", re.IGNORECASE)


def load_json(path):
    """Load a UTF-8 JSON file."""
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def normalize_question(question):
    """Normalize a question to detect obvious duplicates."""
    return re.sub(r"\s+", " ", question.strip().lower())


def validate(target_path, source_path=None):
    """Validate the target dataset and optionally compare original records."""
    errors = []
    warnings = []

    # Load target dataset.
    try:
        records = load_json(target_path)
    except (OSError, json.JSONDecodeError) as exc:
        return [], [f"Cannot read target JSON: {exc}"], warnings

    if not isinstance(records, list):
        return [], ["Dataset root must be a JSON array"], warnings

    if not records:
        errors.append("Dataset is empty")

    # Load original dataset, if provided.
    original_records = None
    original_by_id = {}
    original_ids = set()

    if source_path is not None:
        try:
            original_records = load_json(source_path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"Cannot read original dataset: {exc}")

        if original_records is not None:
            if not isinstance(original_records, list):
                errors.append("Original dataset root must be a JSON array")
                original_records = None
            else:
                for item in original_records:
                    if not isinstance(item, dict):
                        continue

                    record_id = item.get("id")
                    if type(record_id) is int:
                        original_ids.add(record_id)
                        original_by_id[record_id] = item

    ids = []
    questions = []
    category_counts = Counter()

    # Validate every record.
    for index, record in enumerate(records):
        prefix = f"Record {index}"

        if not isinstance(record, dict):
            errors.append(f"{prefix}: record must be a JSON object")
            continue

        # Required fields shared by both old and new records.
        missing_fields = REQUIRED_FIELDS - set(record.keys())
        if missing_fields:
            errors.append(
                f"{prefix}: missing required fields "
                f"{', '.join(sorted(missing_fields))}"
            )

        # ID must be an integer, excluding booleans.
        record_id = record.get("id")

        if type(record_id) is not int:
            errors.append(f"{prefix}: id must be an integer")
        else:
            ids.append(record_id)

        is_original_record = (
            type(record_id) is int and record_id in original_ids
        )

        # Validate question.
        question = record.get("question")
        if not isinstance(question, str) or not question.strip():
            errors.append(f"{prefix}: question must be a non-empty string")
        else:
            questions.append((index, normalize_question(question)))

        # Validate answer.
        answer = record.get("answer")
        if not isinstance(answer, str) or not answer.strip():
            errors.append(f"{prefix}: answer must be a non-empty string")

        # Validate keywords.
        keywords = record.get("keywords")
        if not isinstance(keywords, list):
            errors.append(f"{prefix}: keywords must be a list")
        else:
            if not all(
                isinstance(keyword, str) and keyword.strip()
                for keyword in keywords
            ):
                errors.append(
                    f"{prefix}: every keyword must be a non-empty string"
                )

            normalized_keywords = [
                keyword.strip().lower()
                for keyword in keywords
                if isinstance(keyword, str)
            ]
            if len(normalized_keywords) != len(set(normalized_keywords)):
                warnings.append(
                    f"{prefix}: duplicate keywords detected"
                )

        # Validate category.
        category = record.get("category")
        if not isinstance(category, str) or not category.strip():
            errors.append(f"{prefix}: category must be a non-empty string")
        else:
            category_counts[category] += 1

        # Validate severity.
        severity = record.get("severity")
        if not isinstance(severity, str) or not severity.strip():
            errors.append(f"{prefix}: severity must be a non-empty string")
        elif severity.lower() not in VALID_SEVERITIES:
            warnings.append(
                f"{prefix}: unfamiliar severity value {severity!r}"
            )

        # Validate related questions.
        related_questions = record.get("related_questions")
        if not isinstance(related_questions, list):
            errors.append(
                f"{prefix}: related_questions must be a list"
            )
        elif not all(
            isinstance(item, str) and item.strip()
            for item in related_questions
        ):
            errors.append(
                f"{prefix}: related_questions must contain "
                "non-empty strings"
            )

        # Original records may keep their legacy schema.
        # New records must have the metadata fields.
        if not is_original_record:
            missing_metadata = METADATA_FIELDS - set(record.keys())
            if missing_metadata:
                errors.append(
                    f"{prefix}: missing metadata "
                    f"{', '.join(sorted(missing_metadata))}"
                )

            source_name = record.get("source_name")
            if not isinstance(source_name, str) or not source_name.strip():
                errors.append(
                    f"{prefix}: source_name must be a non-empty string"
                )

            source_url = record.get("source_url")
            if not isinstance(source_url, str) or not URL_PATTERN.match(
                source_url.strip()
            ):
                errors.append(
                    f"{prefix}: source_url must be a valid HTTP(S) URL"
                )

            language = record.get("language")
            if not isinstance(language, str) or not language.strip():
                errors.append(
                    f"{prefix}: language must be a non-empty string"
                )

        # reviewed_at is optional in value, but the field must exist
        # on new records and its value must be null or a non-empty string.
        if "reviewed_at" in record:
            reviewed_at = record["reviewed_at"]
            if reviewed_at is not None and (
                not isinstance(reviewed_at, str)
                or not reviewed_at.strip()
            ):
                errors.append(
                    f"{prefix}: reviewed_at must be null "
                    "or a non-empty string"
                )

    # Check for duplicate IDs.
    duplicate_ids = sorted(
        record_id
        for record_id, count in Counter(ids).items()
        if count > 1
    )
    if duplicate_ids:
        errors.append(f"Duplicate IDs found: {duplicate_ids}")

    # Check for duplicate normalized questions.
    seen_questions = {}
    for index, normalized in questions:
        if normalized in seen_questions:
            errors.append(
                f"Duplicate question detected in records "
                f"{seen_questions[normalized]} and {index}"
            )
        else:
            seen_questions[normalized] = index

    # Compare original records against the target.
    # The original fields and their values must be preserved.
    if original_records is not None:
        target_by_id = {
            record.get("id"): record
            for record in records
            if isinstance(record, dict)
            and type(record.get("id")) is int
        }

        for original_id, original_record in original_by_id.items():
            target_record = target_by_id.get(original_id)

            if target_record is None:
                errors.append(
                    f"Original record ID {original_id} is missing "
                    "from target dataset"
                )
                continue

            for field in REQUIRED_FIELDS:
                if field not in original_record:
                    continue

                if target_record.get(field) != original_record[field]:
                    errors.append(
                        f"Original record ID {original_id}: "
                        f"field {field!r} was changed"
                    )

        # Warn if target contains fewer records than original.
        if len(records) < len(original_records):
            warnings.append(
                "Target dataset contains fewer records than the original"
            )

    return records, errors, warnings, category_counts


def main():
    if len(sys.argv) not in (2, 3):
        print(
            "Usage: python backend/scripts/validate_medical_dataset.py "
            "<target.json> [original.json]"
        )
        return 2

    target_path = Path(sys.argv[1])
    source_path = Path(sys.argv[2]) if len(sys.argv) == 3 else None

    records, errors, warnings, category_counts = validate(
        target_path,
        source_path,
    )

    print(f"Target: {target_path}")
    if source_path is not None:
        print(f"Original: {source_path}")

    if isinstance(records, list):
        print(f"Records: {len(records)}")

        ids = [
            record["id"]
            for record in records
            if isinstance(record, dict)
            and type(record.get("id")) is int
        ]
        print(f"Unique integer IDs: {len(set(ids))}")

        if category_counts:
            print("By category:")
            for category, count in sorted(category_counts.items()):
                print(f"  {category}: {count}")

    for warning in warnings:
        print(f"WARNING: {warning}")

    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1

    print("STRUCTURE VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
