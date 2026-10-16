from app.rag.rejection_experiments import (
    apply_method,
    explicitly_supports_relation,
    explain_relation_decision,
)


def test_answer_semantic_check_keeps_relevant_context_and_rejects_topic_only_match():
    positive = {"id": 35, "answer": "High blood sugar can cause thirst and blurred vision."}
    unrelated = {"id": 33, "answer": "Hypertension means blood pressure is too high."}
    ranked = [(positive, .72), (unrelated, .68)]
    result = apply_method("B", ranked, {35: .76, 33: .31})
    assert [doc["id"] for doc, _ in result] == [35]


def test_covered_medical_answer_remains_retrievable_with_semantic_check():
    source = {"id": 35, "answer": "High blood sugar can cause thirst and blurred vision."}
    result = apply_method("B", [(source, .72)], {35: .76})
    assert result == [(source, .72)]


def test_answer_reranking_prefers_answer_similarity_within_original_candidates():
    docs = [{"id": 1}, {"id": 2}]
    result = apply_method("C", [(docs[0], .8), (docs[1], .7)], {1: .25, 2: .72})
    assert [doc["id"] for doc, _ in result] == [2, 1]


def test_relation_guard_rejects_two_thematically_close_but_unrelated_records():
    pressure = {"id": 33, "answer": "Hypertension is high blood pressure."}
    glucose = {"id": 35, "answer": "High blood sugar can cause thirst."}
    assert not explicitly_supports_relation([pressure, glucose], "causal_pressure_glucose")
    result = apply_method("D", [(pressure, .72), (glucose, .69)], relation_profile="causal_pressure_glucose")
    assert result == []


def test_relation_guard_only_accepts_explicit_relation_in_one_answer():
    evidence = {"id": 99, "answer": "High blood pressure causes elevated blood sugar."}
    assert explicitly_supports_relation([evidence], "causal_pressure_glucose")


def test_supported_comparison_in_corpus_is_not_rejected():
    source = {
        "id": 5,
        "answer": (
            "Flu symptoms usually begin suddenly. Cold symptoms tend to develop more gradually. "
            "Symptoms can overlap, so this comparison cannot confirm a diagnosis."
        ),
    }
    result = apply_method("D", [(source, .78)], relation_profile="compare_flu_cold")
    assert result == [(source, .78)]


def test_unsupported_relation_exposes_partial_sources_without_resolving_relation():
    pressure = {"id": 33, "answer": "Hypertension means blood pressure is consistently high."}
    glucose = {"id": 35, "answer": "High blood sugar can cause thirst and blurred vision."}
    ranked = [(pressure, .73), (glucose, .70)]
    decision = explain_relation_decision(ranked, "causal_pressure_glucose")
    assert decision["documents"] == []
    assert {doc["id"] for doc in decision["partial_documents"]} == {33, 35}
    assert decision["supporting_evidence"] == []
    assert decision["uncertainty"] == "high"
    assert apply_method("D", ranked, relation_profile="causal_pressure_glucose") == []


def test_causal_words_in_separate_sentences_do_not_create_relation_evidence():
    doc = {"id": 77, "answer": "Hypertension affects blood pressure. Hyperglycemia can cause thirst."}
    assert not explicitly_supports_relation([doc], "causal_pressure_glucose")


def test_supported_symptom_association_remains_available():
    source = {"id": 32, "answer": "Common symptoms of diabetes can include increased thirst."}
    result = apply_method("D", [(source, .72)], relation_profile="association_diabetes_thirst")
    assert result == [(source, .72)]


def test_explicit_negation_is_reported_as_denial_not_affirmative_support():
    from app.rag.rejection_experiments import explain_relation_decision

    source = {"id": 99, "answer": "Hypertension does not cause high blood sugar."}
    decision = explain_relation_decision([(source, .72)], "causal_pressure_glucose")
    assert decision["documents"] == [source]
    assert decision["supporting_evidence"][0]["sentences"][0]["polarity"] == "denied"

