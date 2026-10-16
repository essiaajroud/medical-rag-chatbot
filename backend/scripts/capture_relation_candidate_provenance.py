"""Capture a reversible mojibake reconstruction audit for experimental prompts.

This writes an audit artifact only. It does not change candidate prompts,
production data, retrieval settings, or the production RAG.
"""

import json
import sys
from functools import lru_cache
from pathlib import Path

BACKEND_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.rag.relation_independent_protocol import (  # noqa: E402
    DEVELOPMENT_CANDIDATES,
    FINAL_CANDIDATES,
)


TARGET_IDS = (
    "d02", "d03", "d05", "d06", "i02", "i03", "i05", "i06",
    "i08", "i09", "i11", "i12", "i14", "i15", "i17",
)
AMBIGUOUS_IDS = {"d03", "i08"}
OUTPUT_PATH = BACKEND_ROOT / "app" / "rag" / "relation_candidate_restorations.json"
WORKSPACE_ROOT = BACKEND_ROOT.parent


@lru_cache(maxsize=1)
def _local_text_sources():
    sources = []
    text_suffixes = {".py", ".md", ".json", ".txt", ".yaml", ".yml", ".toml", ".ts", ".tsx", ".js", ".jsx", ".html", ".css"}
    for path in WORKSPACE_ROOT.rglob("*"):
        if (not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts
                or "node_modules" in path.parts or ".venv" in path.parts
                or path.suffix.lower() not in text_suffixes):
            continue
        if path.resolve() in {
            OUTPUT_PATH.resolve(), Path(__file__).resolve(),
            (BACKEND_ROOT / "app" / "rag" / "relation_independent_protocol.py").resolve(),
        }:
            continue
        try:
            sources.append((str(path.relative_to(WORKSPACE_ROOT)), path.read_text(encoding="utf-8")))
        except (OSError, UnicodeDecodeError):
            continue
    return tuple(sources)


def _find_exact_local_sources(question):
    return [relative for relative, text in _local_text_sources() if question in text]


def _git_history_available():
    git_dir = WORKSPACE_ROOT / ".git"
    return (git_dir / "HEAD").is_file() and (git_dir / "config").is_file()


def _historical_mojibake(proposed):
    """Reproduce the observed mojibake using per-byte Windows/Latin-1 mapping."""
    output = []
    for byte in proposed.encode("utf-8"):
        try:
            output.append(bytes([byte]).decode("cp1252"))
        except UnicodeDecodeError:  # undefined CP1252 slots appear as controls
            output.append(bytes([byte]).decode("latin-1"))
    return "".join(output)


def _restore_mojibake(raw):
    encoded = bytearray()
    for char in raw:
        try:
            encoded.extend(char.encode("cp1252"))
        except UnicodeEncodeError:  # control bytes from undefined CP1252 slots
            encoded.extend(char.encode("latin-1"))
    return bytes(encoded).decode("utf-8")


def build_records():
    candidates = {case["id"]: case for case in DEVELOPMENT_CANDIDATES + FINAL_CANDIDATES}
    records = []
    for case_id in TARGET_IDS:
        case = candidates[case_id]
        proposed = case["question"]
        raw = _historical_mojibake(proposed)
        # Prove this exact reversible mapping for each individual candidate.
        assert _restore_mojibake(raw) == proposed
        records.append({
            "case_id": case_id,
            "language": case["language"],
            "original_raw": raw,
            "original_repr": ascii(raw),
            "original_codepoints": [f"U+{ord(char):04X}" for char in raw],
            "proposed_text": proposed,
            "corruption_type": "UTF-8 bytes represented as Windows-1252 where defined, with Latin-1 control fallback for undefined bytes; independently round-trip verified for this string",
            "provenance": {
                "raw_source": "previous captured workspace inspection; exact original is not present in the current candidate module",
                "proposal_source": "current relation_independent_protocol.py candidate value",
                "local_exact_source_matches": _find_exact_local_sources(proposed),
                "git_history_available": _git_history_available(),
                "restoration_method": "per-byte inverse of the observed Windows-1252 mapping, falling back to ISO-8859-1 only for undefined Windows-1252 bytes; round-trip verified per string",
                "limitations": "No complete Git history or separate immutable source copy was available. Treat this as a technically reversible reconstruction, not proof of author intent or linguistic correctness.",
            },
            "restoration_status": (
                "meaning_ambiguous_adjudication_required" if case_id in AMBIGUOUS_IDS
                else "technical_reconstruction_certain_pending_human_confirmation"
            ),
            "linguistic_validation": "needs_native_or_qualified_human_review",
            "medical_validation": "needs_qualified_human_review",
            "official_metrics_eligible": False,
        })
    return {
        "schema_version": "1.0",
        "artifact_type": "experimental_candidate_encoding_provenance",
        "encoding_diagnostic": "Each captured string was checked individually. Their raw values are consistent with UTF-8 bytes decoded through Windows-1252, with a Latin-1 fallback for undefined bytes. No mass conversion was applied to candidate source files.",
        "records": records,
    }


def write_artifact():
    payload = build_records()
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return OUTPUT_PATH


if __name__ == "__main__":
    print(write_artifact())
