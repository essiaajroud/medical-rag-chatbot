from app.rag.relation_generalization_benchmark import FINAL_CASES, validate_split_isolation
from app.rag.relation_intent import detect_relation_intent
from app.rag.rejection_experiments import explain_relation_decision


def test_detector_reads_only_question_and_finds_some_multilingual_relations():
    cases = {case["id"]: case for case in FINAL_CASES}
    assert detect_relation_intent(cases["f05"]["question"])["profile"] == "causal_illness_glucose"
    assert detect_relation_intent(cases["f13"]["question"])["profile"] == "causal_pressure_glucose"
    assert detect_relation_intent(cases["f15"]["question"])["profile"] == "causal_pressure_glucose"
    assert detect_relation_intent(cases["f17"]["question"])["profile"] == "association_pressure_glucose"


def test_single_topic_request_is_information_not_relation():
    query = next(case["question"] for case in FINAL_CASES if case["id"] == "f21")
    result = detect_relation_intent(query)
    assert result["intent"] == "simple_information"
    assert result["profile"] is None


def test_vague_or_unspecified_relation_abstains():
    for case_id in ("f24", "f25", "f26"):
        query = next(case["question"] for case in FINAL_CASES if case["id"] == case_id)
        assert detect_relation_intent(query)["intent"] == "indeterminate"


def test_final_wordings_are_disjoint_from_development_wordings():
    assert validate_split_isolation()


def test_partial_context_for_unsupported_relation_never_validates_it():
    cases = {case["id"]: case for case in FINAL_CASES}
    case = cases["f13"]
    docs = [
        {"id": 33, "answer": "Hypertension is consistently high blood pressure."},
        {"id": 35, "answer": "High blood sugar can cause thirst and blurred vision."},
    ]
    decision = explain_relation_decision(
        [(doc, 0.8) for doc in docs], case["manual_profile"]
    )
    assert not decision["documents"]
    assert {doc["id"] for doc in decision["partial_documents"]} == case["partial_document_ids"]
    assert decision["supporting_evidence"] == []


def test_current_error_audit_reproduces_misses_without_changing_detector_rules():
    from scripts.audit_relation_intent import build_report

    _, errors, _ = build_report()
    assert len(errors) == 15
    assert sum(row["category"] == "comparison_missed" for row in errors) == 6
    assert sum(row["category"] == "simple_false_relation" for row in errors) == 0


def test_new_independent_candidates_stay_unscored_until_review_and_use_disjoint_families():
    from app.rag.relation_independent_protocol import (
        FINAL_CANDIDATES, DECISION_THRESHOLDS, validate_protocol_splits,
    )

    assert validate_protocol_splits()
    assert {case["language"] for case in FINAL_CANDIDATES} == {"en", "fr", "ar"}
    assert all(case["annotation_status"].startswith("needs_independent") for case in FINAL_CANDIDATES)
    assert all(case["gold_intent"] is None and case["relevant_document_ids"] is None for case in FINAL_CANDIDATES)
    assert DECISION_THRESHOLDS["relation_false_positive_rate_max"] == 0.05


def test_f10_alternative_is_separate_and_does_not_mutate_original_annotation():
    from app.rag.relation_generalization_benchmark import F10_CAUSAL_ALTERNATIVE

    original = next(case for case in FINAL_CASES if case["id"] == "f10")
    assert original["relation_type"] == "association"
    assert original["relevant_document_ids"] == {32}
    assert F10_CAUSAL_ALTERNATIVE["relation_type"] == "causal"
    assert F10_CAUSAL_ALTERNATIVE["relevant_document_ids"] == frozenset()
    assert F10_CAUSAL_ALTERNATIVE["partial_document_ids"] == {32}
    assert F10_CAUSAL_ALTERNATIVE["validation_status"] == "requires_clinical_review"


def test_f10_sensitivity_recounts_covered_and_insufficient_cases_separately():
    from scripts.rag_relation_generalization_eval import evaluate_method

    predictions = {case["id"]: detect_relation_intent(case["question"]) for case in FINAL_CASES}
    retrieval = {case["id"]: [] for case in FINAL_CASES}
    alternative = evaluate_method("D", FINAL_CASES, retrieval, predictions, 2, f10_alternative=True)
    assert alternative["positive_query_count"] == 14
    assert alternative["insufficient_relation_query_count"] == 9
    original = evaluate_method("D", FINAL_CASES, retrieval, predictions, 2)
    assert original["positive_query_count"] == 15
    assert original["insufficient_relation_query_count"] == 8


def test_historical_evaluation_is_labeled_exploratory_and_not_official():
    from app.rag.relation_independent_protocol import official_cases

    assert official_cases(FINAL_CASES) == ()


def test_official_gate_requires_two_validated_reviews_and_adjudication():
    from app.rag.relation_independent_protocol import is_officially_validated

    case = {
        "annotation_status": "validated",
        "reviews": [
            {"status": "submitted", "linguistic_validation": "validated", "medical_validation": "validated"},
            {"status": "submitted", "linguistic_validation": "validated", "medical_validation": "validated"},
        ],
        "adjudication_status": "not_needed_agreement",
        "gold_intent": "relation",
        "relation_type": "causal_direct",
        "evidence_level": "direct",
        "relevant_document_ids": [3],
        "partial_document_ids": [],
        "irrelevant_document_ids": [8],
    }
    assert is_officially_validated(case)
    assert not is_officially_validated({**case, "reviews": case["reviews"][:1]})
    assert not is_officially_validated({**case, "adjudication_status": "not_started"})
    assert not is_officially_validated({**case, "reviews": [case["reviews"][0], {**case["reviews"][1], "medical_validation": "needs_validation"}]})


def test_evaluator_reports_annotated_prediction_oracle_and_document_partitions_separately():
    from scripts.rag_relation_generalization_eval import evaluate_method

    case = next(case for case in FINAL_CASES if case["id"] == "f13")
    predictions = {case["id"]: detect_relation_intent(case["question"])}
    retrieval = {case["id"]: [({"id": doc_id}, 0.8) for doc_id in (33, 35, 1)]}
    rows = evaluate_method("D", (case,), retrieval, predictions, 3)["errors"]
    row = rows[0]
    assert row["profile_source"] == "manual_oracle"
    assert row["annotated_intent"] == "relation"
    assert row["predicted_intent"] == predictions[case["id"]]["intent"]
    assert row["reference_proof_document_ids"] == []
    assert row["reference_partial_context_document_ids"] == [33, 35]
    assert row["reference_irrelevant_document_ids"] == []
    assert row["retrieved_document_partition"]["irrelevant_document_ids"] == [1]
    assert row["evidence_partition"]["partial_context_document_ids"] == []


def test_evaluator_identifies_e_profile_as_automatic_not_oracle():
    from scripts.rag_relation_generalization_eval import evaluate_method

    case = FINAL_CASES[0]
    predictions = {case["id"]: detect_relation_intent(case["question"])}
    rows = evaluate_method("E", (case,), {case["id"]: []}, predictions, 2)["errors"]
    assert rows[0]["profile_source"] == "predicted_by_E"


def test_candidate_restoration_artifact_preserves_raw_values_and_provenance():
    import json
    from pathlib import Path
    from scripts.capture_relation_candidate_provenance import TARGET_IDS, _restore_mojibake

    artifact = Path(__file__).parents[1] / "app" / "rag" / "relation_candidate_restorations.json"
    payload = json.loads(artifact.read_text(encoding="utf-8"))
    records = {record["case_id"]: record for record in payload["records"]}
    assert set(records) == set(TARGET_IDS)
    for record in records.values():
        assert _restore_mojibake(record["original_raw"]) == record["proposed_text"]
        assert record["original_repr"] == ascii(record["original_raw"])
        assert len(record["original_codepoints"]) == len(record["original_raw"])
        assert record["original_codepoints"] == [
            f"U+{ord(char):04X}" for char in record["original_raw"]
        ]
        assert record["provenance"]["restoration_method"]
        assert record["provenance"]["proposal_source"]
        assert record["restoration_status"] in {
            "technical_reconstruction_certain_pending_human_confirmation",
            "meaning_ambiguous_adjudication_required",
        }
        assert record["linguistic_validation"] != "validated"
        assert record["medical_validation"] != "validated"
        assert record["official_metrics_eligible"] is False


def test_restored_candidates_are_not_mojibake_but_raw_snapshots_are_detectable():
    import json
    from pathlib import Path

    artifact = Path(__file__).parents[1] / "app" / "rag" / "relation_candidate_restorations.json"
    records = json.loads(artifact.read_text(encoding="utf-8"))["records"]
    markers = ("Ã", "Â", "�", "Ù", "Ø")
    for record in records:
        assert any(marker in record["original_raw"] for marker in markers)
        assert not any(marker in record["proposed_text"] for marker in markers)


def test_nonvalidated_restoration_cases_remain_excluded_from_official_metrics():
    import json
    from pathlib import Path
    from app.rag.relation_independent_protocol import official_cases

    artifact = Path(__file__).parents[1] / "app" / "rag" / "relation_candidate_restorations.json"
    records = json.loads(artifact.read_text(encoding="utf-8"))["records"]
    assert official_cases(records) == ()


def test_human_review_bundle_is_blinded_and_does_not_modify_production_dataset():
    import hashlib
    from pathlib import Path
    from app.rag.relation_independent_protocol import official_cases
    from scripts.build_relation_human_review_dossier import build_review_bundle

    backend = Path(__file__).parents[1]
    dataset = backend / "data" / "data_enriched_v3.json"
    before = hashlib.sha256(dataset.read_bytes()).hexdigest()
    bundle = build_review_bundle()
    after = hashlib.sha256(dataset.read_bytes()).hexdigest()
    assert before == after
    for packet_name in ("evaluator_1", "evaluator_2"):
        packet = bundle[packet_name]
        assert len(packet["forms"]) == 15
        assert all("prediction_blinding_notice" in form for form in packet["forms"])
        assert all("expected_answer" in form and form["expected_answer"] == "" for form in packet["forms"])
        assert all("predictions" not in form and "oracle_profile" not in form for form in packet["forms"])
        assert official_cases(packet["forms"]) == ()


def test_review_bundle_leaves_decisions_blank_and_documents_as_unverified_leads():
    from scripts.build_relation_human_review_dossier import build_review_bundle

    bundle = build_review_bundle()
    assert len(bundle["dossiers"]) == 15
    for dossier in bundle["dossiers"]:
        assert dossier["linguistic_validation"] == "needs_validation"
        assert dossier["medical_validation"] == "needs_validation"
        assert dossier["official_metrics_eligible"] is False
        assert all(doc["status"] == "candidate_for_manual_content_check_not_evidence"
                   for doc in dossier["possible_documents_for_inspection_not_evidence"])
    assert bundle["adjudication"]["adjudicator_code"] == ""
    assert all(row["decision"] == "" for row in bundle["adjudication"]["cases"])
    assert {row["case_id"] for row in bundle["dossiers"] if row["case_id"] in {"d03", "i08", "i17"}} == {"d03", "i08", "i17"}

