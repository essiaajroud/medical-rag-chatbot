"""Pre-registered protocol and unadjudicated candidates for independent review.

Nothing in this file is consumed by the detector or the production RAG. Gold
annotations intentionally remain null until an independent bilingual/clinical
reviewer has checked intent, source evidence, and translations.
"""


PROTOCOL_VERSION = "1.0-prospectively-frozen"

ANNOTATION_CRITERIA = {
    "intent": "relation only when the question asks how two explicitly identified concepts relate; simple information for a single topic; indeterminate for missing entities or unspecified relation semantics.",
    "relation_proof": "a source must state the requested direction/type and qualify it; co-occurrence, shared topic, or separate facts are context only.",
    "partial_context": "one or more entities are supported but the requested relation, scope, or clinical condition is not.",
    "insufficient": "mark not demonstrated by the supplied corpus; never annotate the real-world relation as false on that basis.",
    "medical_validation": "a qualified reviewer must verify medical meaning and evidence level; native speakers must review FR/AR meaning and dialect/register before gold labels are frozen.",
    "adjudication": "two independent annotators; disagreements go to a third adjudicator. Preserve original labels and log every change with a reason.",
}

METRIC_DEFINITIONS = {
    "recall_at_k": "mean per-query fraction of gold relevant documents present in returned top k; exclude cases with no validated gold documents.",
    "precision_at_k": "mean per-query relevant documents divided by k; use the same k and queries for A/D/E.",
    "mrr": "mean reciprocal rank of the first gold relevant document over validated covered queries.",
    "relation_false_positive_rate": "insufficient/partial relation cases where method returns a relation-claiming evidence document divided by all validated insufficient/partial relation cases.",
    "covered_false_rejection_rate": "covered relation cases where method returns no relation-proving gold document divided by validated covered relation cases.",
    "intent_metrics": "precision, recall, macro-F1 and 3x3 confusion matrix for relation/simple/indeterminate; report per language and relation type.",
}

# Gates are fixed before independent gold labels/results exist. These are
# prospective study criteria, not fitted to the current final-set scores.
DECISION_THRESHOLDS = {
    "intent_macro_f1_min": 0.80,
    "relation_intent_recall_min": 0.85,
    "relation_intent_precision_min": 0.90,
    "per_language_relation_recall_min": 0.75,
    "relation_false_positive_rate_max": 0.05,
    "covered_false_rejection_rate_max": 0.10,
    "E_recall_at_2_drop_vs_A_max": 0.02,
    "E_precision_at_2_gain_vs_A_min": 0.05,
}

# Publication gates fixed before the independent labels are collected. Since
# the final prompts include translated members of the same semantic families,
# counts for inference are family-level, not raw question-level counts.
PUBLICATION_RULES = {
    "exploratory": "Historical A/D/E results remain descriptive and are never presented as independent confirmation.",
    "development": "Use only the six development items for workflow calibration or method changes; publish counts and label status.",
    "final": "Freeze code, threshold, corpus snapshot, and adjudicated labels before one final run; any post-inspection change requires a new final set.",
    "official_label_gate": "Only cases with two independent annotations, adjudication when needed, and language/medical validation statuses validated may enter official metrics.",
    "minimum_independent_families_for_confirmatory_claim": 30,
    "minimum_subgroup_n_for_inference": 10,
    "subgroup_unit": "semantic family; translated variants are not independent units",
}


def is_officially_validated(case):
    """Fail closed: require gold status plus two reviews and adjudication state."""
    reviews = case.get("reviews") or (case.get("annotation_1"), case.get("annotation_2"))
    reviews = tuple(review for review in reviews if review is not None)
    if case.get("annotation_status") != "validated" or len(reviews) != 2:
        return False
    if any(review.get("status") != "submitted" for review in reviews):
        return False
    if any(review.get("linguistic_validation") != "validated" for review in reviews):
        return False
    if any(review.get("medical_validation") != "validated" for review in reviews):
        return False
    adjudication = case.get("adjudication") or {}
    adjudication_status = case.get("adjudication_status", adjudication.get("decision"))
    if adjudication_status not in {"not_needed_agreement", "adjudicated"}:
        return False
    reference = adjudication if adjudication_status == "adjudicated" else case
    required = (
        reference.get("final_intent", reference.get("gold_intent")),
        reference.get("final_relation_type_and_direction", reference.get("relation_type")),
        reference.get("final_expected_evidence_level", reference.get("evidence_level")),
        reference.get("final_proof_document_ids", reference.get("relevant_document_ids")),
        reference.get("final_partial_context_document_ids", reference.get("partial_document_ids")),
        reference.get("final_irrelevant_document_ids", reference.get("irrelevant_document_ids")),
    )
    return all(value is not None for value in required)


def official_cases(cases):
    """Return only cases with a complete, validated reference; never infer gold."""
    return tuple(case for case in cases if is_officially_validated(case))


def _candidate(case_id, split, question, language, family, concepts, relation_type=None):
    return {
        "id": case_id,
        "split": split,
        "question": question,
        "language": language,
        "family": family,
        "concepts": tuple(concepts),
        "candidate_relation_type": relation_type,
        "gold_intent": None,
        "relevant_document_ids": None,
        "partial_document_ids": None,
        "evidence_level": None,
        "annotation_status": "needs_independent_clinical_and_language_validation",
    }


# Development candidates are for annotation workflow calibration only. No
# detector tuning may use the final items or their labels.
DEVELOPMENT_CANDIDATES = (
    _candidate("d01", "development", "Can an infection bring on a fever?", "en", "infection_fever", ("infection", "fever"), "causal"),
    _candidate("d02", "development", "La soif peut-elle accompagner le diabète ?", "fr", "diabetes_thirst", ("diabetes", "thirst"), "association"),
    _candidate("d03", "development", "هل تتغير أعراض الإنفلونزا عن الزكام؟", "ar", "flu_cold", ("flu", "cold"), "comparison"),
    _candidate("d04", "development", "What does elevated blood sugar mean?", "en", "glucose_simple", ("glucose",)),
    _candidate("d05", "development", "Quels signes accompagnent la déshydratation ?", "fr", "dehydration_simple", ("dehydration",)),
    _candidate("d06", "development", "هل يمكن أن يرفع المرض السكر مؤقتا؟", "ar", "illness_glucose", ("illness", "glucose"), "causal"),
)


# These final prompts use relation families not present as pairs in the current
# detector profile inventory. Their truth/evidence labels are deliberately blank.
FINAL_CANDIDATES = (
    _candidate("i01", "final", "Could a prescribed medicine make glucose rise temporarily?", "en", "medication_glucose", ("medication", "glucose"), "causal_indirect"),
    _candidate("i02", "final", "Un médicament prescrit peut-il faire augmenter temporairement la glycémie ?", "fr", "medication_glucose", ("medication", "glucose"), "causal_indirect"),
    _candidate("i03", "final", "هل يمكن لدواء موصوف أن يرفع سكر الدم مؤقتا؟", "ar", "medication_glucose", ("medication", "glucose"), "causal_indirect"),
    _candidate("i04", "final", "Might dehydration contribute to feeling unusually tired?", "en", "dehydration_fatigue", ("dehydration", "fatigue"), "causal_indirect"),
    _candidate("i05", "final", "La déshydratation pourrait-elle contribuer à une fatigue inhabituelle ?", "fr", "dehydration_fatigue", ("dehydration", "fatigue"), "causal_indirect"),
    _candidate("i06", "final", "هل قد يساهم الجفاف في الشعور بالتعب؟", "ar", "dehydration_fatigue", ("dehydration", "fatigue"), "causal_indirect"),
    _candidate("i07", "final", "Is blurred vision associated with high blood glucose?", "en", "glucose_vision", ("glucose", "vision"), "association"),
    _candidate("i08", "final", "La vision floue est-elle associée à une glycémie élevée ?", "fr", "glucose_vision", ("glucose", "vision"), "association"),
    _candidate("i09", "final", "هل يرتبط تشوش الرؤية بارتفاع سكر الدم؟", "ar", "glucose_vision", ("glucose", "vision"), "association"),
    _candidate("i10", "final", "How do flu symptoms compare with COVID symptoms?", "en", "flu_covid", ("flu", "covid"), "comparison"),
    _candidate("i11", "final", "Comment comparer les symptômes de la grippe et de la COVID ?", "fr", "flu_covid", ("flu", "covid"), "comparison"),
    _candidate("i12", "final", "كيف تختلف أعراض الإنفلونزا عن أعراض كوفيد؟", "ar", "flu_covid", ("flu", "covid"), "comparison"),
    _candidate("i13", "final", "What symptoms can occur with anemia?", "en", "anemia_simple", ("anemia",)),
    _candidate("i14", "final", "Quels symptômes peuvent accompagner une anémie ?", "fr", "anemia_simple", ("anemia",)),
    _candidate("i15", "final", "ما الأعراض التي قد ترافق فقر الدم؟", "ar", "anemia_simple", ("anemia",)),
    _candidate("i16", "final", "Do these conditions affect one another?", "en", "unspecified_entities", (), None),
    _candidate("i17", "final", "هل توجد علاقة بينهما؟", "ar", "unspecified_entities", (), None),
)


def validate_protocol_splits():
    dev_families = {case["family"] for case in DEVELOPMENT_CANDIDATES}
    final_families = {case["family"] for case in FINAL_CANDIDATES}
    questions = [case["question"].casefold().strip() for case in DEVELOPMENT_CANDIDATES + FINAL_CANDIDATES]
    return not (dev_families & final_families) and len(questions) == len(set(questions))
