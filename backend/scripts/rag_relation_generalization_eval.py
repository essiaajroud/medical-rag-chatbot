"""Offline A/D/E evaluation on a separate, newly authored final split."""

import contextlib
import io
import json
import os
import sys
import argparse
from collections import Counter, defaultdict
from pathlib import Path

BACKEND_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import RAG_CONTEXT_THRESHOLD
from app.rag.rejection_experiments import apply_method, explain_relation_decision
from app.rag.relation_generalization_benchmark import (
    FINAL_CASES, F10_CAUSAL_ALTERNATIVE, validate_split_isolation,
)
from app.rag.relation_intent import detect_relation_intent
from app.rag.relation_independent_protocol import official_cases


def intent_metrics(cases, predictions):
    labels = ("relation", "simple_information", "indeterminate")
    confusion = {actual: {predicted: 0 for predicted in labels} for actual in labels}
    for case in cases:
        expected = case["expected_intent"]
        predicted = predictions[case["id"]]["intent"]
        confusion[expected][predicted] += 1
    def summarize(matrix):
        per_class = {}
        for label in labels:
            tp = matrix[label][label]
            fp = sum(matrix[actual][label] for actual in labels if actual != label)
            fn = sum(matrix[label][predicted] for predicted in labels if predicted != label)
            precision = tp / (tp + fp) if tp + fp else 0.0
            recall = tp / (tp + fn) if tp + fn else 0.0
            per_class[label] = {
                "precision": precision if tp + fp else None,
                "recall": recall if tp + fn else None,
                "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0,
                "support": sum(matrix[label].values()),
            }
        return {"confusion_matrix_actual_rows": matrix, "per_class": per_class,
                "macro_f1": sum(row["f1"] for row in per_class.values()) / len(labels)}

    output = summarize(confusion)
    by_language = {}
    by_relation_type = {}
    for group_name, selector, destination in (
        ("language", lambda case: case["language"], by_language),
        ("relation_type", lambda case: case["relation_type"] or "none", by_relation_type),
    ):
        values = defaultdict(lambda: {actual: {predicted: 0 for predicted in labels} for actual in labels})
        for case in cases:
            values[selector(case)][case["expected_intent"]][predictions[case["id"]]["intent"]] += 1
        destination.update({name: summarize(matrix) for name, matrix in sorted(values.items())})
    output["by_language"] = by_language
    output["by_relation_type"] = by_relation_type
    return output


def evaluate_method(method, cases, retrieval, predictions, k, f10_alternative=False):
    if f10_alternative:
        cases = tuple(
            {
                **case,
                "expected_intent": F10_CAUSAL_ALTERNATIVE["expected_intent"],
                "relation_type": F10_CAUSAL_ALTERNATIVE["relation_type"],
                "relevant_document_ids": F10_CAUSAL_ALTERNATIVE["relevant_document_ids"],
                "partial_document_ids": F10_CAUSAL_ALTERNATIVE["partial_document_ids"],
                "evidence_level": F10_CAUSAL_ALTERNATIVE["evidence_level"],
                "manual_profile": None,
            } if case["id"] == "f10" else case
            for case in cases
        )
    recalls, precisions, reciprocal_ranks = [], [], []
    positives = [case for case in cases if case["relevant_document_ids"]
                 and case["expected_intent"] != "indeterminate"]
    insufficient = [case for case in cases if not case["relevant_document_ids"] and case["expected_intent"] == "relation"]
    false_rejections = false_positives = 0
    by_language = defaultdict(lambda: {"retrieval_recall": [], "false_positive": [], "false_rejection": []})
    by_relation = defaultdict(lambda: {"count": 0, "retrieval_hits": 0, "false_positives": 0, "insufficient": 0})
    errors = []

    for case in cases:
        ranked = retrieval[case["id"]]
        profile = case["manual_profile"] if method == "D" else None
        if method == "E":
            predicted = predictions[case["id"]]
            profile = predicted["profile"] if predicted["intent"] == "relation" else None
            if predicted["intent"] == "indeterminate":
                selected = []  # abstain and request clarification
            else:
                selected = apply_method("D", ranked, relation_profile=profile,
                                        threshold=RAG_CONTEXT_THRESHOLD)
        elif method == "D" and f10_alternative and case["id"] == "f10":
            # The alternative is a causal question. Existing oracle association
            # profile cannot prove causality; under this alternative, D returns
            # no relation evidence (without asserting that causality is false).
            selected = []
        elif method == "D":
            selected = apply_method("D", ranked, relation_profile=profile,
                                    threshold=RAG_CONTEXT_THRESHOLD)
        else:
            selected = [(doc, score) for doc, score in ranked
                        if float(score) >= RAG_CONTEXT_THRESHOLD]

        top = selected[:k]
        ids = [doc["id"] for doc, _ in top]
        gold = case["relevant_document_ids"]
        hits = len(set(ids) & gold)
        if gold and case["expected_intent"] != "indeterminate":
            recalls.append(hits / len(gold))
            precisions.append(hits / k)
            rank = next((position for position, doc_id in enumerate(ids, 1) if doc_id in gold), None)
            reciprocal_ranks.append(1 / rank if rank else 0.0)
            rejected = hits == 0
            false_rejections += rejected
            by_language[case["language"]]["retrieval_recall"].append(hits / len(gold))
            by_language[case["language"]]["false_rejection"].append(bool(rejected))
        elif not gold and case["expected_intent"] == "relation":
            by_language[case["language"]]["false_positive"].append(bool(top))
        relation_type = case["relation_type"] or "none"
        group = by_relation[relation_type]
        group["count"] += 1
        if gold and case["expected_intent"] != "indeterminate":
            group["retrieval_hits"] += bool(hits)
        elif case["expected_intent"] == "relation":
            group["insufficient"] += 1
            group["false_positives"] += bool(top)
        false_positives += bool(not gold and bool(top) and case["expected_intent"] == "relation")

        verifier = None
        if case["manual_profile"]:
            verifier = explain_relation_decision(ranked, case["manual_profile"], RAG_CONTEXT_THRESHOLD)
        evidence_partition = None
        retrieved_partition = {
            "relation_proving_document_ids": sorted(
                doc["id"] for doc, _ in ranked if doc["id"] in case["relevant_document_ids"]
            ),
            "partial_context_document_ids": sorted(
                doc["id"] for doc, _ in ranked if doc["id"] in case["partial_document_ids"]
            ),
            "irrelevant_document_ids": sorted(
                doc["id"] for doc, _ in ranked
                if doc["id"] not in (case["relevant_document_ids"] | case["partial_document_ids"])
            ),
        }
        if case["manual_profile"] or case["expected_intent"] == "indeterminate":
            proof_ids = set(case["relevant_document_ids"])
            partial_ids = set(case["partial_document_ids"])
            evidence_partition = {
                "relation_proving_document_ids": sorted(doc_id for doc_id in ids if doc_id in proof_ids),
                "partial_context_document_ids": sorted(doc_id for doc_id in ids if doc_id in partial_ids),
                "irrelevant_document_ids": sorted(doc_id for doc_id in ids if doc_id not in proof_ids | partial_ids),
            }
        errors.append({
            "id": case["id"], "question": case["question"], "language": case["language"],
            "annotated_intent": case["expected_intent"],
            "predicted_intent": predictions[case["id"]]["intent"],
            "detected_intent": predictions[case["id"]]["intent"],  # legacy report field
            "profile_source": "manual_oracle" if method == "D" else ("predicted_by_E" if method == "E" else "none"),
            "expected_profile": case["manual_profile"], "predicted_profile": predictions[case["id"]]["profile"],
            "reference_proof_document_ids": sorted(gold),
            "reference_partial_context_document_ids": sorted(case["partial_document_ids"]),
            "reference_irrelevant_document_ids": sorted(
                set(ids) - set(gold) - set(case["partial_document_ids"])
            ),
            "expected_documents": sorted(gold),  # legacy report field
            "returned_documents": ids,
            "scores": [{"id": doc["id"], "score": round(float(score), 4)} for doc, score in top],
            "false_positive": bool(not gold and bool(top) and case["expected_intent"] == "relation"),
            "false_rejection": bool(gold and case["expected_intent"] != "indeterminate" and hits == 0),
            "verifier_reason_oracle_profile": verifier["reason"] if verifier else None,
            "partial_context_ids_oracle_profile": sorted(doc["id"] for doc in verifier["partial_documents"]) if verifier else [],
            "evidence_partition": evidence_partition,
            "retrieved_document_partition": retrieved_partition,
        })

    fpr = false_positives / len(insufficient) if insufficient else None
    fnr = false_rejections / len(positives) if positives else None
    return {
        "positive_query_count": len(positives), "insufficient_relation_query_count": len(insufficient),
        "recall_at_k": sum(recalls) / len(recalls) if recalls else None,
        "precision_at_k": sum(precisions) / len(precisions) if precisions else None,
        "mrr": sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else None,
        "false_positive_rate_insufficient_relation": fpr,
        "false_rejection_rate_covered": fnr,
        "by_language": {
            lang: {
                "recall": sum(v["retrieval_recall"]) / len(v["retrieval_recall"]) if v["retrieval_recall"] else None,
                "false_positive_rate": sum(v["false_positive"]) / len(v["false_positive"]) if v["false_positive"] else None,
                "false_rejection_rate": sum(v["false_rejection"]) / len(v["false_rejection"]) if v["false_rejection"] else None,
            } for lang, v in sorted(by_language.items())
        },
        "by_relation_type": {
            name: {"questions": v["count"], "positive_retrieval_rate": v["retrieval_hits"] / max(1, v["count"] - v["insufficient"]),
                  "insufficient_evidence_false_positive_rate": v["false_positives"] / v["insufficient"] if v["insufficient"] else None}
            for name, v in sorted(by_relation.items())
        },
        "errors": errors,
    }


def main():
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    from app.data.loader import load_data
    from app.vectorstore.faiss_store import FAISSStore

    if not validate_split_isolation():
        raise RuntimeError("Development and final questions overlap after normalization")
    data_path = BACKEND_ROOT / "data" / "data_enriched_v3.json"
    records = load_data(data_path)
    retrieval = {}
    with contextlib.redirect_stdout(io.StringIO()):
        store = FAISSStore(records)
        for case in FINAL_CASES:
            scores, docs = store.search(case["question"], len(records))
            retrieval[case["id"]] = list(zip(docs, map(float, scores)))

    predictions = {case["id"]: detect_relation_intent(case["question"]) for case in FINAL_CASES}
    metrics = {
        method: {f"@{k}": evaluate_method(method, FINAL_CASES, retrieval, predictions, k)
                 for k in (2, 5)}
        for method in ("A", "D", "E")
    }
    f10_alternative_metrics = {
        method: {f"@{k}": evaluate_method(
            method, FINAL_CASES, retrieval, predictions, k, f10_alternative=True
        ) for k in (2, 5)}
        for method in ("A", "D", "E")
    }
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true", help="Include every annotation and question-level output")
    parser.add_argument("--summary", action="store_true", help="Print compact A/D/E and f10 sensitivity metrics")
    args = parser.parse_args()
    report = {
        "result_classification": "exploratory_historical_not_independent_confirmation",
        "official_metrics": False,
        "official_validated_case_count": len(official_cases(FINAL_CASES)),
        "official_exclusion_reason": "These historical cases were not collected through the blinded double-annotation and adjudication protocol.",
        "dataset": data_path.name, "record_count": len(records), "threshold": RAG_CONTEXT_THRESHOLD,
        "split": "final", "case_count": len(FINAL_CASES),
        "development_case_count": 4, "exact_question_overlap": False,
        "intention_metrics": intent_metrics(FINAL_CASES, predictions),
        "metrics": metrics,
        "f10_annotation_sensitivity": {
            "original_annotation": {
                "expected_intent": "relation", "relation_type": "association",
                "relevant_document_ids": [32], "evidence_level": "explicit",
                "metrics": metrics,
            },
            "alternative_annotation": {
                **{key: (sorted(value) if isinstance(value, frozenset) else value)
                   for key, value in F10_CAUSAL_ALTERNATIVE.items()},
                "metrics": f10_alternative_metrics,
            },
            "interpretation": "Corpus insufficiency for this causal claim is not evidence that the medical relation is false. D uses no causal proof for this one alternative case; the current oracle inventory only has the symptom-association profile.",
        },
        "detector_misses_sample": [
            {"id": case["id"], "question": case["question"],
             "predicted_intent": predictions[case["id"]]["intent"]}
            for case in FINAL_CASES
            if case["expected_intent"] == "relation"
            and predictions[case["id"]]["intent"] != "relation"
        ][:8],
        "representative_failures_at_2": {
            method: [{"id": row["id"], "question": row["question"],
                      "expected_documents": row["expected_documents"],
                      "returned_documents": row["returned_documents"],
                      "false_positive": row["false_positive"],
                      "false_rejection": row["false_rejection"],
                      "detected_intent": row["detected_intent"],
                      "predicted_profile": row["predicted_profile"]}
                     for row in metrics[method]["@2"]["errors"]
                     if row["false_positive"] or row["false_rejection"]][:6]
            for method in ("A", "D", "E")
        },
        "interpretation": "Synthetic held-out wording authored for this evaluation; target facts overlap the small production corpus. No Gemini generation evaluated.",
    }
    if args.full:
        report["detector_predictions"] = predictions
        report["annotations"] = [
            {**case, "concepts": list(case["concepts"]),
             "relevant_document_ids": sorted(case["relevant_document_ids"]),
             "partial_document_ids": sorted(case["partial_document_ids"])}
            for case in FINAL_CASES
        ]
    else:
        metric_groups = [report["metrics"],
                         report["f10_annotation_sensitivity"]["alternative_annotation"]["metrics"]]
        for group in metric_groups:
            for method_data in group.values():
                for cutoff_data in method_data.values():
                    cutoff_data.pop("errors", None)
    if args.summary:
        metric_keys = (
            "positive_query_count", "insufficient_relation_query_count", "recall_at_k",
            "precision_at_k", "mrr", "false_positive_rate_insufficient_relation",
            "false_rejection_rate_covered", "by_language", "by_relation_type",
        )
        def compact(group):
            return {method: {cutoff: {key: vals[key] for key in metric_keys}
                             for cutoff, vals in method_values.items()}
                    for method, method_values in group.items()}
        report["metrics"] = compact(metrics)
        report["f10_annotation_sensitivity"]["original_annotation"]["metrics"] = compact(metrics)
        report["f10_annotation_sensitivity"]["alternative_annotation"]["metrics"] = compact(f10_alternative_metrics)
        report.pop("representative_failures_at_2", None)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import contextlib
    main()
