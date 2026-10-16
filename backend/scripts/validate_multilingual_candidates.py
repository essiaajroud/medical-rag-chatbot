"""Validate the separate, unreviewed multilingual candidate dataset."""

import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

from langdetect import DetectorFactory

BACKEND = Path(__file__).parents[1]
sys.path.insert(0, str(BACKEND))
from app.core.language_utils import detect_language


DetectorFactory.seed = 0
ORIGINAL_PATH = BACKEND / "data" / "data_enriched_v3.json"
CANDIDATE_PATH = BACKEND / "data" / "data_multilingual_candidates.json"
REQUIRED = {
    "id", "question", "answer", "keywords", "category", "severity",
    "related_questions", "source_name", "source_url", "reviewed_at", "language",
}


def normalize_question(text):
    text = unicodedata.normalize("NFKD", text.casefold())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^\w]+", " ", text, flags=re.UNICODE).strip()


def validate(originals, candidates):
    errors = []
    if not isinstance(originals, list) or not isinstance(candidates, list):
        return ["Both files must contain JSON arrays"]
    if candidates[:len(originals)] != originals:
        errors.append("Original records must be preserved unchanged at the start of the candidate file")
    if len(candidates) != len(originals) * 3:
        errors.append(f"Expected 3 language versions per source record; found {len(candidates)} records")
    ids = [record.get("id") for record in candidates if isinstance(record, dict)]
    if len(ids) != len(candidates) or len(ids) != len(set(ids)):
        errors.append("Candidate record IDs must be present and unique")
    if set(ids) != set(range(len(candidates))):
        errors.append("Candidate record IDs must be contiguous from 0")

    seen_questions = set()
    for index, record in enumerate(candidates):
        if not isinstance(record, dict):
            errors.append(f"Record {index} is not an object")
            continue
        missing = REQUIRED - record.keys()
        if missing:
            errors.append(f"Record {index} missing fields: {', '.join(sorted(missing))}")
            continue
        language = record["language"]
        if language not in {"en", "fr", "ar"}:
            errors.append(f"Record {index}: unsupported language code {language!r}")
        if not isinstance(record["keywords"], list) or not isinstance(record["related_questions"], list):
            errors.append(f"Record {index}: keywords and related_questions must be arrays")
        question = record["question"]
        if not isinstance(question, str) or not question.strip():
            errors.append(f"Record {index}: question must be a non-empty string")
        else:
            duplicate_key = (language, normalize_question(question))
            if duplicate_key in seen_questions:
                errors.append(f"Duplicate question in {language}: {question}")
            seen_questions.add(duplicate_key)
        url = record["source_url"]
        try:
            parsed = urlparse(url) if isinstance(url, str) else None
            if not parsed or parsed.scheme not in {"http", "https"} or not parsed.hostname:
                errors.append(f"Record {index}: source_url is not a valid HTTP(S) URL")
        except ValueError:
            errors.append(f"Record {index}: source_url is malformed")
        if record["reviewed_at"] is not None:
            errors.append(f"Record {index}: candidate/original reviewed_at must remain null")

        content = f"{record.get('question', '')} {record.get('answer', '')}"
        detected = detect_language(content)
        if detected != language:
            errors.append(f"Record {index}: declared language {language!r} conflicts with detected {detected!r}")

    for original_index, original in enumerate(originals):
        for offset, language in enumerate(("fr", "ar"), start=1):
            candidate_index = len(originals) + original_index * 2 + offset - 1
            if candidate_index >= len(candidates):
                continue
            candidate = candidates[candidate_index]
            if candidate.get("language") != language:
                errors.append(f"Record {candidate_index}: expected {language} translation of source ID {original['id']}")
            for field in ("category", "severity", "source_name", "source_url"):
                if candidate.get(field) != original.get(field):
                    errors.append(f"Record {candidate_index}: {field} differs from source ID {original['id']}")
    return errors


def main():
    originals = json.loads(ORIGINAL_PATH.read_text(encoding="utf-8"))
    candidates = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    errors = validate(originals, candidates)
    print(f"Original records: {len(originals)}; candidate corpus: {len(candidates)}")
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print("VALID (translation entries remain unreviewed candidates)")


if __name__ == "__main__":
    main()
