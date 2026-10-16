"""Offline, annotated retrieval benchmark.

Run from backend with ``python scripts/rag_eval.py``. Compare the separate
candidate corpus using ``python scripts/rag_eval.py --candidate data/data_multilingual_candidates.json``.
The model must be cached locally; the script disables network access.
"""

import argparse
import contextlib
import io
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

BACKEND_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import RAG_CONTEXT_THRESHOLD
from app.rag.retrieval_experiments import apply_strategy


CASES = (
    {"query": "What are the signs of high blood sugar?", "language": "en", "intent": "medical", "relevant_ids": {32, 35}},
    {"query": "Quels sont les signes d’une glycémie élevée ?", "language": "fr", "intent": "medical", "relevant_ids": {32, 35}},
    {"query": "ما هي أعراض ارتفاع السكر في الدم؟", "language": "ar", "intent": "medical", "relevant_ids": {32, 35}},
    {"query": "Does high blood sugar always mean diabetes?", "language": "en", "intent": "medical", "relevant_ids": {36}},
    {"query": "Can high blood sugar occur without diabetes?", "language": "en", "intent": "medical", "relevant_ids": {36}},
    {"query": "What is hyperglycemia?", "language": "en", "intent": "medical", "relevant_ids": {34, 35, 36}},
    {"query": "Quels sont les symptômes du diabète ?", "language": "fr", "intent": "medical", "relevant_ids": {32}},
    {"query": "What symptoms can frequent thirst and urination indicate?", "language": "en", "intent": "medical", "relevant_ids": {32, 35}},
    {"query": "Explain diabetes symptoms and blood glucose", "language": "en", "intent": "medical", "relevant_ids": {32, 34, 35}},
    {"query": "What are symptoms and prevention of dehydration?", "language": "en", "intent": "medical", "relevant_ids": {4, 30}},
    {"query": "What are symptoms and causes of flu?", "language": "en", "intent": "medical", "relevant_ids": {1, 5}},
    {"query": "I feel exhausted", "language": "en", "intent": "medical", "relevant_ids": {10}},
    {"query": "What are the symptoms of lupus?", "language": "en", "intent": "medical", "relevant_ids": set()},
    {"query": "How is multiple sclerosis treated?", "language": "en", "intent": "medical", "relevant_ids": set(), "annotation": "not covered"},
    {"query": "What insulin dose should I take for type 1 diabetes?", "language": "en", "intent": "medical", "relevant_ids": set(), "annotation": "not covered: dosage"},
    {"query": "Can hypertension cause hyperglycemia?", "language": "en", "intent": "medical", "relevant_ids": set(), "annotation": "not covered: causal relationship"},
    {"query": "How do I create a Python class?", "language": "en", "relevant_ids": None, "route": "out_of_scope"},
    {"query": "I have chest pain and difficulty breathing.", "language": "en", "relevant_ids": None, "route": "emergency"},
    {"query": "Is it bad?", "language": "en", "relevant_ids": None, "route": "unclear"},
)


def calculate_metrics(cases, results, k, threshold):
    """Calculate scores only where a human supplied relevant source IDs."""
    ranked = [case for case in cases if case["relevant_ids"]]
    recalls, precisions, reciprocal_ranks = [], [], []
    by_language = defaultdict(list)
    language_matches = defaultdict(lambda: [0, 0])
    no_answer_cases = [case for case in cases if case["relevant_ids"] == set()]

    for case in ranked:
        docs, scores = results[case["query"]]
        top_docs = list(zip(docs, scores))[:k]
        ids = [doc.get("_canonical_id", doc["id"]) for doc, _ in top_docs]
        relevant = case["relevant_ids"]
        # Several language variants map to one canonical source record; count
        # that concept once so duplicates cannot inflate recall or precision.
        found = len(set(ids) & relevant)
        recalls.append(found / len(relevant))
        precisions.append(found / k)
        rank = next((i for i, doc_id in enumerate(ids, 1) if doc_id in relevant), None)
        reciprocal_ranks.append(1 / rank if rank else 0.0)
        by_language[case["language"]].append(recalls[-1])
        for doc, _ in top_docs:
            language_matches[case["language"]][1] += 1
            language_matches[case["language"]][0] += (
                doc.get("_retrieved_language", case["language"]) == case["language"]
            )

    no_answer_hits = sum(
        any(float(score) >= threshold for score in results[case["query"]][1][:k])
        for case in no_answer_cases
    )
    positive_without_context = sum(
        not any(float(score) >= threshold for score in results[case["query"]][1][:k])
        for case in ranked
    )
    return {
        "annotated_query_count": len(ranked),
        "recall_at_k": sum(recalls) / len(recalls) if recalls else None,
        "precision_at_k": sum(precisions) / len(precisions) if precisions else None,
        "mrr": sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else None,
        "no_relevant_document_queries": len(no_answer_cases),
        "no_relevant_document_rate": no_answer_hits / len(no_answer_cases) if no_answer_cases else None,
        "positive_queries_without_context_rate": (
            positive_without_context / len(ranked) if ranked else None
        ),
        "recall_by_language": {
            lang: sum(values) / len(values) for lang, values in sorted(by_language.items())
        },
        "retrieved_language_match_at_k": {
            lang: matched / total for lang, (matched, total) in sorted(language_matches.items()) if total
        },
    }


def evaluate_dataset(data_path, candidate=False, strategy="A"):
    from app.data.loader import load_data
    from app.vectorstore.faiss_store import FAISSStore

    records = load_data(data_path)
    ids = {record["id"] for record in records}
    for case in CASES:
        missing = (case["relevant_ids"] or set()) - set(range(37))
        if missing:
            raise ValueError(f"Unknown canonical relevance IDs {sorted(missing)}")
    store = FAISSStore(records)
    results = {}
    routing_cases = {case["query"] for case in CASES if case.get("route")}
    for case in CASES:
        if case["query"] in routing_cases:
            continue
        scores, docs = store.search(case["query"], len(records))
        prepared = []
        for doc in docs:
            item = dict(doc)
            if candidate and item["id"] >= 37:
                # Candidate IDs are appended in source-record order: FR then AR.
                item["_canonical_id"] = (item["id"] - 37) // 2
            else:
                item["_canonical_id"] = item["id"]
            item["_retrieved_language"] = item.get("language", "en")
            prepared.append(item)
        ranked = list(zip(prepared, scores))
        results[case["query"]] = ([doc for doc, _ in ranked], [score for _, score in ranked])
    return records, results


def results_for_strategy(raw_results, strategy):
    results = {}
    for case in CASES:
        query = case["query"]
        if query not in raw_results:
            continue
        docs, scores = raw_results[query]
        ranked = apply_strategy(
            list(zip(docs, scores)), strategy, case.get("language", "en"),
            RAG_CONTEXT_THRESHOLD, candidate=True,
        )
        results[query] = ([doc for doc, _ in ranked], [score for _, score in ranked])
    return results


def metrics_by_k(results):
    return {
        f"@{k}": calculate_metrics(CASES, results, k, RAG_CONTEXT_THRESHOLD)
        for k in (2, 5)
    }


def main():
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, help="Compare a full candidate corpus against production data")
    parser.add_argument("--strategy", choices=("A", "B", "C", "D", "all"), default="A", help="Experimental retrieval strategy")
    args = parser.parse_args()

    original_path = BACKEND_ROOT / "data" / "data_enriched_v3.json"
    with contextlib.redirect_stdout(io.StringIO()):
        original_records, before_results = evaluate_dataset(original_path, strategy="A")
    from app.agent import classify_question, detect_emergency_type

    routing = {}
    for case in CASES:
        expected = case.get("intent", case.get("route"))
        if not expected:
            continue
        actual = classify_question(case["query"])
        if expected == "emergency":
            actual = "emergency" if detect_emergency_type(case["query"]) else "not_emergency"
        routing[case["query"]] = {"expected": expected, "actual": actual, "passed": expected == actual}

    before = {
        "dataset_count": len(original_records),
        "metrics": metrics_by_k(before_results),
        "routing_checks": routing,
    }
    if args.candidate:
        with contextlib.redirect_stdout(io.StringIO()):
            candidate_records, raw_candidate_results = evaluate_dataset(args.candidate, candidate=True)
        strategies = ("A", "B", "C", "D") if args.strategy == "all" else (args.strategy,)
        experimental_results = {
            strategy: metrics_by_k(results_for_strategy(raw_candidate_results, strategy))
            for strategy in strategies
        }
        after_results = results_for_strategy(raw_candidate_results, strategies[0])
        if args.strategy == "all":
            report = {
                "benchmark": {"positive_queries": 12, "negative_or_unanswerable_queries": 4, "k": [2, 5], "threshold": RAG_CONTEXT_THRESHOLD},
                "baseline_A": before["metrics"],
                "candidate_corpus_count": len(candidate_records),
                "metrics_by_strategy": experimental_results,
                "negative_case_top_results": {
                    strategy: {
                        case["query"]: [
                            {"id": doc["id"], "source_id": doc["_canonical_id"], "language": doc["_retrieved_language"], "score": round(float(score), 4)}
                            for doc, score in list(zip(*results_for_strategy(raw_candidate_results, strategy)[case["query"]]))[:2]
                            if float(score) >= RAG_CONTEXT_THRESHOLD
                        ]
                        for case in CASES if case["relevant_ids"] == set()
                    }
                    for strategy in strategies
                },
            }
        else:
            report = {
            "questions_and_canonical_relevance_annotations": "identical before and after",
            "before": before,
            "after": {
                "dataset_count": len(candidate_records),
                "strategy": args.strategy,
                "metrics": experimental_results[strategies[0]] if len(strategies) == 1 else None,
                "metrics_by_strategy": experimental_results if len(strategies) > 1 else None,
                "retrieved_top_5": {
                    query: [
                        {
                            "id": doc["id"],
                            "canonical_id": doc["_canonical_id"],
                            "language": doc["_retrieved_language"],
                            "score": round(float(score), 4),
                        }
                        for doc, score in list(zip(docs, scores))[:5]
                    ]
                    for query, (docs, scores) in after_results.items()
                    if query in {
                        "What are the signs of high blood sugar?",
                        "Quels sont les signes d’une glycémie élevée ?",
                        "ما هي أعراض ارتفاع السكر في الدم؟",
                        "What are the symptoms of lupus?",
                    }
                },
            },
            }
    else:
        report = before
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
