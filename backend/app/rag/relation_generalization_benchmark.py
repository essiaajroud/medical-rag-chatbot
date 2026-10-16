"""Newly authored development/final cases; kept separate from the historical 52."""


def _case(case_id, question, language, intent, relation, concepts, relevant,
          evidence, expected, rationale, profile=None, split="final", partial=()):
    return {
        "id": case_id, "question": question, "language": language,
        "expected_intent": intent, "relation_type": relation,
        "concepts": tuple(concepts), "relevant_document_ids": frozenset(relevant),
        "partial_document_ids": frozenset(partial),
        "evidence_level": evidence, "expected_response": expected,
        "rationale": rationale, "manual_profile": profile, "split": split,
    }


# Development questions are used only for detector iteration and are excluded
# from all reported final metrics. They intentionally use their own phrasing.
DEV_CASES = (
    _case("dev-causal-en", "Can an infection bring on a fever?", "en", "relation", "causal", ("infection", "fever"), {0, 6}, "explicit", "Answer with qualification", "The corpus says infections often cause fever.", "causal_infection_fever", "dev"),
    _case("dev-assoc-en", "Does diabetes come with increased thirst?", "en", "relation", "association", ("diabetes", "thirst"), {32}, "explicit", "Answer as a possible symptom, not a diagnosis", "Record 32 lists increased thirst.", "association_diabetes_thirst", "dev"),
    _case("dev-compare-en", "How is influenza unlike a cold?", "en", "relation", "comparison", ("flu", "cold"), {5}, "explicit", "Compare documented onset and overlap", "Record 5 compares flu and cold.", "compare_flu_cold", "dev"),
    _case("dev-simple-en", "What does hyperglycemia mean?", "en", "simple_information", None, ("glucose",), {34, 35, 36}, "context", "Define from available records", "One concept is requested; this is information seeking.", split="dev"),
)


# Final prompts are held apart from development examples and historical prompts.
# Their target facts necessarily overlap the small production corpus; wording does not.
FINAL_CASES = (
    _case("f01", "What might set off a fever when someone has an infection?", "en", "relation", "causal", ("infection", "fever"), {0, 6}, "explicit", "Explain that infections can cause fever, with qualification", "Both source records state this causal direction.", "causal_infection_fever"),
    _case("f02", "Une infection est-elle susceptible de déclencher de la fièvre ?", "fr", "relation", "causal", ("infection", "fever"), {0, 6}, "explicit", "Répondre avec la nuance présente dans les sources", "Les deux fiches relient les infections à la fièvre.", "causal_infection_fever"),
    _case("f03", "هل يمكن أن تؤدي العدوى إلى الحمى؟", "ar", "relation", "causal", ("infection", "fever"), {0, 6}, "explicit", "ذكر العلاقة مع التحفظ الوارد في المصادر", "تذكر المادتان أن العدوى قد تسبب الحمى.", "causal_infection_fever"),
    _case("f04", "Could being sick push glucose upward for a short time?", "en", "relation", "causal", ("illness", "glucose"), {36}, "explicit", "State that illness may temporarily raise glucose", "Record 36 explicitly lists illness as a temporary cause.", "causal_illness_glucose"),
    _case("f05", "Une maladie peut-elle entraîner une hausse passagère du sucre sanguin ?", "fr", "relation", "causal", ("illness", "glucose"), {36}, "explicit", "Répondre avec les causes temporaires citées", "La fiche 36 relie explicitement la maladie à une hausse temporaire.", "causal_illness_glucose"),
    _case("f06", "هل قد يرفع المرض مستوى السكر لفترة وجيزة؟", "ar", "relation", "causal", ("illness", "glucose"), {36}, "explicit", "ذكر أن المرض قد يرفع السكر مؤقتا", "تذكر المادة 36 هذا السبب المؤقت.", "causal_illness_glucose"),
    _case("f07", "Which clues help tell influenza apart from an ordinary cold?", "en", "relation", "comparison", ("flu", "cold"), {5}, "explicit", "Compare onset and symptom overlap; avoid diagnosis", "Record 5 explicitly compares these illnesses.", "compare_flu_cold"),
    _case("f08", "Par quels éléments la grippe se démarque-t-elle d’un rhume banal ?", "fr", "relation", "comparison", ("flu", "cold"), {5}, "explicit", "Comparer le début et le chevauchement des symptômes", "La fiche 5 décrit ces différences et leur chevauchement.", "compare_flu_cold"),
    _case("f09", "ما العلامات التي تميز الإنفلونزا عن الزكام العادي؟", "ar", "relation", "comparison", ("flu", "cold"), {5}, "explicit", "مقارنة بداية الأعراض مع التنبيه إلى تداخلها", "المادة 5 تقارن بين الحالتين.", "compare_flu_cold"),
    _case("f10", "Is unusual thirst one of the things diabetes can cause?", "en", "relation", "association", ("diabetes", "thirst"), {32}, "explicit", "Say it can be a symptom but cannot diagnose diabetes", "Record 32 lists increased thirst as a possible symptom.", "association_diabetes_thirst"),
    _case("f11", "La soif inhabituelle peut-elle accompagner le diabète ?", "fr", "relation", "association", ("diabetes", "thirst"), {32}, "explicit", "Présenter cela comme un symptôme possible, pas un diagnostic", "La fiche 32 inclut la soif parmi les symptômes possibles.", "association_diabetes_thirst"),
    _case("f12", "هل يمكن أن يكون العطش الزائد من علامات السكري؟", "ar", "relation", "association", ("diabetes", "thirst"), {32}, "explicit", "ذكر أنه عرض محتمل وليس تشخيصا", "تدرج المادة 32 العطش ضمن الأعراض الممكنة.", "association_diabetes_thirst"),
    _case("f13", "Do high blood pressure and raised blood sugar have a proven cause-and-effect link here?", "en", "relation", "causal", ("pressure", "glucose"), set(), "none", "Do not infer a link; explain the corpus lacks evidence", "Records mention each topic separately, not their causal relationship.", "causal_pressure_glucose", partial={33, 35}),
    _case("f14", "La tension élevée peut-elle faire grimper la glycémie ?", "fr", "relation", "causal", ("pressure", "glucose"), set(), "none", "Ne pas conclure à une causalité; signaler le manque de preuve", "Les fiches décrivent séparément la tension et la glycémie.", "causal_pressure_glucose", partial={33, 35}),
    _case("f15", "هل يؤدي ارتفاع ضغط الدم إلى زيادة سكر الدم؟", "ar", "relation", "causal", ("pressure", "glucose"), set(), "none", "عدم تأكيد العلاقة وبيان أن المصادر لا تثبتها", "المعلومات عن الضغط والسكر منفصلة.", "causal_pressure_glucose", partial={33, 35}),
    _case("f16", "Might blood pressure influence someone's glucose readings?", "en", "relation", "causal", ("pressure", "glucose"), set(), "none", "Do not assert; distinguish separate context from proof", "The corpus does not connect these concepts causally.", "causal_pressure_glucose", partial={33, 35}),
    _case("f17", "Does the corpus establish an association between hypertension and hyperglycemia?", "en", "relation", "association", ("pressure", "glucose"), set(), "none", "Say no relation is established by the supplied sources", "Separate mentions do not demonstrate an association.", "association_pressure_glucose", partial={33, 35}),
    _case("f18", "La grippe et la déshydratation donnent-elles des symptômes comparables ?", "fr", "relation", "comparison", ("flu", "dehydration"), set(), "context", "Do not compare; sources provide separate symptom context only", "Records 1 and 4 discuss symptoms separately without comparing them.", "compare_flu_dehydration", partial={1, 4}),
    _case("f19", "Are the warning signs of flu interchangeable with those of dehydration?", "en", "relation", "comparison", ("flu", "dehydration"), set(), "context", "Do not claim equivalence or difference", "The corpus describes both but does not compare them.", "compare_flu_dehydration", partial={1, 4}),
    _case("f20", "هل تتشابه أعراض الإنفلونزا والجفاف؟", "ar", "relation", "comparison", ("flu", "dehydration"), set(), "context", "عدم استنتاج تشابه؛ المعلومات منفصلة", "لا توجد مقارنة مباشرة في السجلات.", "compare_flu_dehydration", partial={1, 4}),
    _case("f21", "What does dehydration feel like?", "en", "simple_information", None, ("dehydration",), {4}, "context", "List symptoms in record 4", "A single-topic symptom request is not a cross-concept relation.",),
    _case("f22", "Quels signes peut-on observer avec une glycémie élevée ?", "fr", "simple_information", None, ("glucose",), {32, 35}, "context", "Summarize the documented signs", "A one-concept symptom question asks for information.",),
    _case("f23", "ما معنى ارتفاع سكر الدم؟", "ar", "simple_information", None, ("glucose",), {34, 35, 36}, "context", "Explain only what the records define", "Single-concept definition request.",),
    _case("f24", "Do these two conditions affect each other?", "en", "indeterminate", None, (), set(), "none", "Ask which conditions the user means", "The entities and relation are unspecified.",),
    _case("f25", "Can fever and infection be connected somehow?", "en", "indeterminate", None, ("infection", "fever"), set(), "ambiguous", "Clarify the kind of relationship rather than assume causality", "The wording permits several relation types without specifying one.", partial={0, 6}),
    _case("f26", "Could blood sugar and blood pressure be related in some way?", "en", "indeterminate", None, ("pressure", "glucose"), set(), "context", "State that this corpus does not establish a relation; clarify if needed", "Relation type is vague; individual context is not proof.", partial={33, 35}),
    _case("f27", "How do I write a Python function?", "en", "simple_information", None, (), set(), "none", "Out of medical scope", "Out-of-domain control; must not be routed to medical relation verification."),
)


# Kept outside FINAL_CASES so the original annotation and reported historical
# figures remain immutable. This is a sensitivity-analysis proposal, not truth.
F10_CAUSAL_ALTERNATIVE = {
    "case_id": "f10",
    "expected_intent": "relation",
    "relation_type": "causal",
    "relevant_document_ids": frozenset(),
    "partial_document_ids": frozenset({32}),
    "evidence_level": "causality_not_established_by_this_corpus",
    "expected_response": "Do not assert causality; state that document 32 supports symptom context only.",
    "validation_status": "requires_clinical_review",
}


ALL_CASES = DEV_CASES + FINAL_CASES


def validate_split_isolation():
    """Ensure no exact prompt or normalized wording is shared across splits."""
    from app.rag.rejection_experiments import normalize
    dev = {normalize(case["question"]) for case in DEV_CASES}
    final = {normalize(case["question"]) for case in FINAL_CASES}
    return not (dev & final)
