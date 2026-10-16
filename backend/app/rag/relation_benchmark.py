"""Hand-annotated multilingual retrieval/relation benchmark grounded in corpus IDs."""


def _case(query, language, category, gold, claims, sufficient, expected,
          relation=None, relation_category=None, partial_ids=(), route=None):
    row = {
        "q": query, "lang": language, "class": category, "gold": set(gold) if gold is not None else None,
        "claims": claims, "corpus_sufficient": sufficient, "expected_behavior": expected,
        "partial_ids": set(partial_ids),
    }
    if relation:
        row["relation"] = relation
        row["relation_category"] = relation_category
    if route:
        row["route"] = route
    return row


CASES = (
    _case("What are the signs of high blood sugar?", "en", "covered", {32, 35},
          ["symptoms listed in the diabetes and hyperglycemia records"], True, "answer"),
    _case("Quels sont les signes d’une glycémie élevée ?", "fr", "covered", {32, 35},
          ["symptoms listed in diabetes and hyperglycemia records"], True, "answer"),
    _case("ما هي أعراض ارتفاع السكر في الدم؟", "ar", "covered", {32, 35},
          ["symptoms listed in diabetes and hyperglycemia records"], True, "answer"),
    _case("Does high blood sugar always mean diabetes?", "en", "covered", {36},
          ["high blood glucose does not always mean diabetes"], True, "answer"),
    _case("Can high blood sugar occur without diabetes?", "en", "covered", {36},
          ["blood glucose can rise for other stated reasons"], True, "answer"),
    _case("What is hyperglycemia?", "en", "covered", {34, 35, 36},
          ["definition and context of glucose and high blood sugar"], True, "answer"),
    _case("Quels sont les symptômes du diabète ?", "fr", "covered", {32},
          ["symptoms listed in the diabetes record"], True, "answer"),
    _case("ما الأعراض الشائعة لمرض السكري؟", "ar", "covered", {32},
          ["symptoms listed in the diabetes record"], True, "answer"),
    _case("What symptoms can frequent thirst and urination indicate?", "en", "covered", {32, 35},
          ["thirst and frequent urination are listed symptoms; they do not confirm diagnosis"], True, "answer"),
    _case("Explain diabetes symptoms and blood glucose", "en", "covered", {32, 34, 35},
          ["symptoms and a basic definition of glucose"], True, "answer"),
    _case("What are symptoms and prevention of dehydration?", "en", "covered", {4, 30},
          ["documented symptoms and prevention steps"], True, "answer"),
    _case("Quels sont les symptômes et comment prévenir la déshydratation ?", "fr", "covered", {4, 30},
          ["documented symptoms and prevention steps"], True, "answer"),
    _case("What are symptoms and causes of flu?", "en", "partially_covered", {1},
          ["common symptoms; the corpus does not state causes"], False, "answer_partially"),
    _case("How can high blood pressure be managed?", "en", "partially_covered", {33},
          ["measurement and professional interpretation; no management plan"], False, "answer_partially"),

    # Short fatigue prompts: same documented concept, paraphrased across languages.
    _case("I feel exhausted", "en", "covered_short_query", {10}, ["fatigue means tiredness or lack of energy"], True, "answer"),
    _case("I have been feeling very tired lately", "en", "covered_short_query", {10}, ["fatigue means tiredness or lack of energy"], True, "answer"),
    _case("Je me sens épuisé et sans énergie", "fr", "covered_short_query", {10}, ["fatigue means tiredness or lack of energy"], True, "answer"),
    _case("أشعر بالتعب والإرهاق", "ar", "covered_short_query", {10}, ["fatigue means tiredness or lack of energy"], True, "answer"),

    # Causality documented in the source answers, including paraphrases.
    _case("Can an infection cause a fever?", "en", "relation_supported", {0, 6}, ["fever is often due to infection; infections can cause fever"], True, "answer", "causal_infection_fever", "causal"),
    _case("Could a fever result from an infection?", "en", "relation_supported_indirect", {0, 6}, ["fever is often due to infection; infections can cause fever"], True, "answer", "causal_infection_fever", "causal"),
    _case("Une infection peut-elle entraîner de la fièvre ?", "fr", "relation_supported", {0, 6}, ["fever is often due to infection; infections can cause fever"], True, "answer", "causal_infection_fever", "causal"),
    _case("هل يمكن أن تسبب العدوى حمى؟", "ar", "relation_supported", {0, 6}, ["fever is often due to infection; infections can cause fever"], True, "answer", "causal_infection_fever", "causal"),
    _case("Can illness temporarily raise blood glucose?", "en", "relation_supported", {36}, ["glucose can rise temporarily because of illness"], True, "answer", "causal_illness_glucose", "causal"),
    _case("La maladie peut-elle faire monter temporairement la glycémie ?", "fr", "relation_supported", {36}, ["glucose can rise temporarily because of illness"], True, "answer", "causal_illness_glucose", "causal"),
    _case("هل يمكن للمرض أن يرفع سكر الدم مؤقتًا؟", "ar", "relation_supported", {36}, ["glucose can rise temporarily because of illness"], True, "answer", "causal_illness_glucose", "causal"),

    # A documented symptom association, distinct from claiming a diagnosis.
    _case("Is thirst a symptom of diabetes?", "en", "association_supported", {32}, ["increased thirst is a possible diabetes symptom"], True, "answer", "association_diabetes_thirst", "association"),
    _case("La soif peut-elle être un symptôme du diabète ?", "fr", "association_supported", {32}, ["increased thirst is a possible diabetes symptom"], True, "answer", "association_diabetes_thirst", "association"),
    _case("هل العطش من أعراض مرض السكري؟", "ar", "association_supported", {32}, ["increased thirst is a possible diabetes symptom"], True, "answer", "association_diabetes_thirst", "association"),

    # The corpus explicitly compares flu and the common cold.
    _case("How do flu symptoms differ from a common cold?", "en", "comparison_supported", {5}, ["flu tends to begin suddenly; cold symptoms develop gradually and overlap"], True, "answer_partially", "compare_flu_cold", "comparison"),
    _case("Quelles différences entre la grippe et le rhume ?", "fr", "comparison_supported", {5}, ["flu tends to begin suddenly; cold symptoms develop gradually and overlap"], True, "answer_partially", "compare_flu_cold", "comparison"),
    _case("هل تختلف أعراض الإنفلونزا عن الزكام؟", "ar", "comparison_supported", {5}, ["flu tends to begin suddenly; cold symptoms develop gradually and overlap"], True, "answer_partially", "compare_flu_cold", "comparison"),

    # The corpus has separate facts about both topics, but no explicit comparison.
    _case("Are flu and dehydration symptoms the same?", "en", "comparison_unsupported", set(), ["do not claim equivalence or difference"], False, "answer_partially", "compare_flu_dehydration", "comparison", {1, 4}),
    _case("Can flu symptoms be distinguished from dehydration?", "en", "comparison_unsupported_paraphrase", set(), ["do not claim equivalence or difference"], False, "answer_partially", "compare_flu_dehydration", "comparison", {1, 4}),
    _case("Les symptômes de la grippe et de la déshydratation sont-ils les mêmes ?", "fr", "comparison_unsupported", set(), ["do not claim equivalence or difference"], False, "answer_partially", "compare_flu_dehydration", "comparison", {1, 4}),
    _case("هل أعراض الإنفلونزا والجفاف متشابهة؟", "ar", "comparison_unsupported", set(), ["do not claim equivalence or difference"], False, "answer_partially", "compare_flu_dehydration", "comparison", {1, 4}),

    # The corpus does not establish a pressure/glucose causal or associative link.
    _case("Can hypertension cause hyperglycemia?", "en", "causal_unsupported", set(), ["do not assert a causal link"], False, "insufficient", "causal_pressure_glucose", "causal", {33, 35}),
    _case("Could high blood pressure lead to high blood sugar?", "en", "causal_unsupported_indirect", set(), ["do not assert a causal link"], False, "insufficient", "causal_pressure_glucose", "causal", {33, 35}),
    _case("L’hypertension peut-elle provoquer une glycémie élevée ?", "fr", "causal_unsupported", set(), ["do not assert a causal link"], False, "insufficient", "causal_pressure_glucose", "causal", {33, 35}),
    _case("La tension artérielle peut-elle influencer le taux de sucre dans le sang ?", "fr", "causal_unsupported_indirect", set(), ["do not assert a causal link"], False, "insufficient", "causal_pressure_glucose", "causal", {33, 35}),
    _case("هل يسبب ارتفاع ضغط الدم ارتفاع السكر في الدم؟", "ar", "causal_unsupported", set(), ["do not assert a causal link"], False, "insufficient", "causal_pressure_glucose", "causal", {33, 35}),
    _case("هل يؤثر ضغط الدم على مستوى السكر في الدم؟", "ar", "causal_unsupported_indirect", set(), ["do not assert a causal link"], False, "insufficient", "causal_pressure_glucose", "causal", {33, 35}),
    _case("Is hypertension associated with hyperglycemia?", "en", "association_unsupported", set(), ["do not assert an association"], False, "insufficient", "association_pressure_glucose", "association", {33, 35}),

    _case("What insulin dose should I take for type 1 diabetes?", "en", "not_covered", set(), ["no insulin dosage is supplied"], False, "insufficient", partial_ids={32}),
    _case("What are the symptoms of lupus?", "en", "not_covered", set(), ["no lupus facts are supplied"], False, "insufficient"),
    _case("How is multiple sclerosis treated?", "en", "not_covered", set(), ["no multiple sclerosis treatment is supplied"], False, "insufficient"),
    _case("Quel traitement prendre contre la sclérose en plaques ?", "fr", "not_covered", set(), ["no multiple sclerosis treatment is supplied"], False, "insufficient"),
    _case("ما جرعة الإنسولين المناسبة؟", "ar", "not_covered", set(), ["no insulin dosage is supplied"], False, "insufficient", partial_ids={32}),
    _case("Is it bad?", "en", "ambiguous", None, ["no medical claim before clarification"], False, "clarify", route="unclear"),
    _case("I have chest pain and difficulty breathing.", "en", "emergency", None,
          ["emergency route takes priority; retrieval guard is bypassed"], False, "emergency", route="emergency"),
    _case("How do I create a Python class?", "en", "out_of_domain", None, ["no medical claim"], False, "out_of_scope", route="out_of_scope"),
    _case("Quelle est la capitale du Japon ?", "fr", "out_of_domain", None, ["no medical claim"], False, "out_of_scope", route="out_of_scope"),
    _case("كيف أكتب برنامج بايثون؟", "ar", "out_of_domain", None, ["no medical claim"], False, "out_of_scope", route="out_of_scope"),
)
