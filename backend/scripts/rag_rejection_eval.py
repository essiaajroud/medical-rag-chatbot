"""Compare retrieval rejection methods offline; this script is not wired into production."""

import contextlib
import io
import json
import os
import sys
import argparse
import time
from collections import defaultdict
from pathlib import Path

BACKEND_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import RAG_CONTEXT_THRESHOLD
from app.rag.rejection_experiments import apply_method, explain_relation_decision


from app.rag.relation_benchmark import CASES


def collect_results(records):
    from app.data.embedding import encode
    from app.vectorstore.faiss_store import FAISSStore

    started = time.perf_counter()
    store = FAISSStore(records)
    retrieval = {}
    medical_cases = [case for case in CASES if case["gold"] is not None]
    for case in medical_cases:
        scores, docs = store.search(case["q"], len(records))
        retrieval[case["q"]] = list(zip(docs, [float(score) for score in scores]))
    retrieval_seconds = time.perf_counter() - started

    semantic_started = time.perf_counter()
    answer_vectors = encode([record.get("answer", "") for record in records])
    query_vectors = encode([case["q"] for case in medical_cases])
    similarities = {}
    for case, query_vector in zip(medical_cases, query_vectors):
        similarities[case["q"]] = {
            record["id"]: float(answer_vectors[index] @ query_vector)
            for index, record in enumerate(records)
        }
    semantic_seconds = time.perf_counter() - semantic_started
    return retrieval, similarities, {
        "store_and_retrieval_seconds": round(retrieval_seconds, 3),
        "answer_and_query_embedding_seconds": round(semantic_seconds, 3),
        "additional_model": "none; existing paraphrase-multilingual-MiniLM-L12-v2",
        "offline": True,
    }


def score_method(method, retrieval, similarities, k):
    positives = [case for case in CASES if case["gold"]]
    negatives = [case for case in CASES if case["gold"] == set()]
    recalls, precisions, reciprocal_ranks = [], [], []
    by_language = defaultdict(list)
    relation_groups = defaultdict(lambda: {"count": 0, "supported": 0, "retrieved_supported": 0,
                                           "unsupported": 0, "unsupported_context": 0})
    false_rejections = false_positives = 0
    errors = []
    for case in CASES:
        if case["gold"] is None:
            continue
        original = retrieval[case["q"]]
        semantic = similarities[case["q"]]
        selected = apply_method(method, original, semantic, case.get("relation"), RAG_CONTEXT_THRESHOLD)
        top = selected[:k]
        retrieved_ids = [doc["id"] for doc, _ in top]
        gold = case["gold"]
        accepted = [doc for doc, score in top if float(score) >= RAG_CONTEXT_THRESHOLD]
        if gold:
            hits = len(set(retrieved_ids) & gold)
            recalls.append(hits / len(gold))
            precisions.append(hits / k)
            rank = next((rank for rank, doc_id in enumerate(retrieved_ids, 1) if doc_id in gold), None)
            reciprocal_ranks.append(1 / rank if rank else 0.0)
            by_language[case["lang"]].append(hits / len(gold))
            rejected = not any(doc["id"] in gold for doc in accepted)
            false_rejections += rejected
        else:
            rejected = False
            false_positives += bool(accepted)
        relation_category = case.get("relation_category")
        if relation_category:
            group = relation_groups[relation_category]
            group["count"] += 1
            if gold:
                group["supported"] += 1
                group["retrieved_supported"] += bool(set(retrieved_ids) & gold)
            else:
                group["unsupported"] += 1
                group["unsupported_context"] += bool(accepted)
        decision = (
            explain_relation_decision(original, case["relation"], RAG_CONTEXT_THRESHOLD)
            if method == "D" and case.get("relation") else None
        )
        errors.append({
            "question": case["q"], "language": case["lang"], "class": case["class"],
            "relation_category": relation_category,
            "claims_required": case["claims"], "corpus_sufficient": case["corpus_sufficient"],
            "expected_behavior": case["expected_behavior"],
            "expected_ids": sorted(gold), "retrieved": [
                {"id": doc["id"], "score": round(float(score), 4),
                 "answer_similarity": round(semantic.get(doc["id"], 0), 4),
                 "accepted": float(score) >= RAG_CONTEXT_THRESHOLD}
                for doc, score in top
            ],
            "false_positive": bool(not gold and accepted),
            "false_rejection": bool(gold and rejected),
            "relation_decision": decision,
            "partial_context_ids": sorted(doc["id"] for doc in decision["partial_documents"]) if decision else [],
        })
    return {
        "positive_query_count": len(positives), "negative_query_count": len(negatives),
        "recall_at_k": sum(recalls) / len(recalls) if recalls else None,
        "precision_at_k": sum(precisions) / len(precisions) if precisions else None,
        "mrr": sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else None,
        "false_positive_rate": false_positives / len(negatives) if negatives else None,
        "false_rejection_rate": false_rejections / len(positives) if positives else None,
        "recall_by_language": {lang: sum(vals) / len(vals) for lang, vals in sorted(by_language.items())},
        "relation_by_category": {
            name: {
                "questions": values["count"],
                "documented_relation_retrieval_rate": (
                    values["retrieved_supported"] / values["supported"] if values["supported"] else None
                ),
                "unsupported_relation_context_rate": (
                    values["unsupported_context"] / values["unsupported"] if values["unsupported"] else None
                ),
            }
            for name, values in sorted(relation_groups.items())
        },
        "errors": errors,
    }


def main():
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    from app.data.loader import load_data
    from app.agent import classify_question

    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", action="store_true", help="Print metrics and question-level errors at @2")
    args = parser.parse_args()

    data_path = BACKEND_ROOT / "data" / "data_enriched_v3.json"
    records = load_data(data_path)
    with contextlib.redirect_stdout(io.StringIO()):
        retrieval, similarities, timing = collect_results(records)
    methods = ("A", "B", "C", "D")
    metrics = {
        method: {f"@{k}": score_method(method, retrieval, similarities, k) for k in (2, 5)}
        for method in methods
    }
    routing = {
        case["q"]: {"expected": case["route"], "actual": classify_question(case["q"]),
                    "passed": case["route"] == classify_question(case["q"])}
        for case in CASES if case.get("route")
    }
    report = {
        "dataset": str(data_path.name), "records": len(records), "threshold": RAG_CONTEXT_THRESHOLD,
        "annotation_counts": {label: sum(case["class"] == label for case in CASES) for label in sorted({case["class"] for case in CASES})},
        "generation_evaluated": False,
        "timing_and_model": timing, "metrics": metrics, "routing_checks": routing,
    }
    if args.summary:
        report["question_level_errors"] = {
            method: {
                "@2": [
                    {"question": error["question"], "class": error["class"],
                     "language": error["language"], "relation_category": error["relation_category"],
                     "expected_ids": error["expected_ids"],
                     "retrieved": [{"id": entry["id"], "score": entry["score"], "accepted": entry["accepted"]} for entry in error["retrieved"]],
                     "false_positive": error["false_positive"],
                     "false_rejection": error["false_rejection"],
                     "relation_decision_reason": error["relation_decision"]["reason"] if error["relation_decision"] else None,
                     "supporting_evidence_ids": [entry["document_id"] for entry in error["relation_decision"]["supporting_evidence"]] if error["relation_decision"] else [],
                     "partial_context_ids": error["partial_context_ids"]}
                    for error in method_metrics["@2"]["errors"]
                    if error["false_positive"] or error["false_rejection"]
                ]
            }
            for method in ("A", "D")
            for method_metrics in (metrics[method],)
        }
        report["metrics"] = {
            method: {
                k: {key: value for key, value in vals.items() if key != "errors"}
                for k, vals in method_metrics.items()
            }
            for method, method_metrics in metrics.items()
        }
    else:
        report["annotations"] = [
            {key: (sorted(value) if isinstance(value, set) else value)
             for key, value in case.items() if key != "gold"}
            | {"gold_ids": sorted(case["gold"]) if case["gold"] is not None else None}
            for case in CASES
        ]
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
