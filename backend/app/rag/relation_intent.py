"""Small, explainable query-only relation intent detector for offline experiments."""

from app.rag.rejection_experiments import normalize


_CONCEPTS = {
    "pressure": ("hypertension", "high blood pressure", "blood pressure", "pression arterielle", "tension arterielle", "tension elevee", "hypertension", "ضغط الدم", "ارتفاع ضغط الدم"),
    "glucose": ("hyperglycemia", "hyperglycaemia", "high blood sugar", "elevated blood sugar", "blood glucose", "blood sugar", "glycemie", "sucre dans le sang", "sucre sanguin", "سكر الدم", "ارتفاع السكر", "جلوكوز", "غلوكوز"),
    "flu": ("influenza", "flu", "grippe", "انفلونزا"),
    "cold": ("common cold", "cold", "rhume", "زكام"),
    "dehydration": ("dehydration", "dehydrated", "deshydratation", "جفاف"),
    "infection": ("infection", "infectious", "infection", "عدوى", "التهاب"),
    "fever": ("fever", "feverish", "temperature", "fievre", "حمى"),
    "illness": ("illness", "illnesses", "disease", "maladie", "مرض"),
    "diabetes": ("diabetes", "diabetic", "diabete", "سكري", "السكري"),
    "thirst": ("thirst", "thirsty", "soif", "عطش"),
}

_RELATION_MARKERS = {
    "causal": (
        "cause", "causes", "caused by", "lead to", "leads to", "result in", "result from", "because of", "due to", "raise", "increase", "affect", "influence",
        "provoquer", "provoque", "entrainer", "entraine", "faire monter", "faire grimper", "augmenter", "influer", "influencer", "a cause de",
        "يسبب", "تسبب", "تؤدي", "يؤدي", "يمكن ان تسبب", "الى", "ترفع", "يزيد", "بسبب",
    ),
    "comparison": (
        "compare", "compared", "difference", "differ", "similar", "same", "versus", "unlike", "distinguish",
        "comparer", "difference", "differ", "semblable", "similaire", "pareil", "identique", "se distinguer",
        "مقارنة", "يختلف", "متشابه", "مثل",
    ),
    "association": (
        "associated with", "association", "correlated", "correlation", "linked to", "related to", "symptom of", "sign of", "include", "including",
        "associe", "association", "correlation", "lie a", "relie a", "symptome de", "signe de", "fait partie",
        "مرتبط", "علاقة", "من اعراض", "عرض من",
    ),
}

_VAGUE_RELATION_MARKERS = (
    "connected", "related", "affect each other", "linked somehow",
    "lie entre", "relie", "agir l un sur l autre", "مرتبط", "علاقة",
)

_PROFILE = {
    frozenset(("pressure", "glucose")): {"causal": "causal_pressure_glucose", "association": "association_pressure_glucose"},
    frozenset(("flu", "dehydration")): {"comparison": "compare_flu_dehydration"},
    frozenset(("flu", "cold")): {"comparison": "compare_flu_cold"},
    frozenset(("diabetes", "thirst")): {"association": "association_diabetes_thirst"},
    frozenset(("infection", "fever")): {"causal": "causal_infection_fever"},
    frozenset(("illness", "glucose")): {"causal": "causal_illness_glucose"},
}


def _contains(normalized, phrase):
    term = normalize(phrase)
    return bool(term and f" {term} " in f" {normalized} ")


def detect_relation_intent(question):
    """Inspect only question text. Low certainty or ambiguous types abstain."""
    normalized = normalize(question)
    concepts = sorted(
        concept for concept, aliases in _CONCEPTS.items()
        if any(_contains(normalized, alias) for alias in aliases)
    )
    found_types = [kind for kind, markers in _RELATION_MARKERS.items()
                   if any(_contains(normalized, marker) for marker in markers)]
    result = {"intent": "simple_information", "relation_type": None,
              "concepts": concepts, "profile": None, "confidence": 0.72 if concepts else 0.55,
              "abstained": False}
    vague_relation = any(_contains(normalized, marker) for marker in _VAGUE_RELATION_MARKERS)
    if (len(concepts) >= 2 and vague_relation) or (len(concepts) < 2 and vague_relation):
        return {**result, "intent": "indeterminate", "confidence": 0.4,
                "abstained": True}
    if len(concepts) < 2 or not found_types:
        return result
    if len(found_types) != 1:
        return {**result, "intent": "indeterminate", "confidence": 0.35,
                "abstained": True}
    relation_type = found_types[0]
    profiles = _PROFILE.get(frozenset(concepts), {})
    profile = profiles.get(relation_type)
    if not profile:
        return {**result, "intent": "indeterminate", "relation_type": relation_type,
                "confidence": 0.4, "abstained": True}
    return {**result, "intent": "relation", "relation_type": relation_type,
            "profile": profile, "confidence": 0.86, "abstained": False}
