"""Offline-only rejection and reranking experiments; never imported by production."""

import re
import unicodedata


THRESHOLD = 0.50


def normalize(text):
    text = unicodedata.normalize("NFKD", str(text).casefold())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^\w]+", " ", text, flags=re.UNICODE)


def answer_similarity_filter(ranked, semantic_scores, threshold=THRESHOLD, candidate_k=5):
    """B: retain retrieval threshold and additionally require answer cosine >= threshold."""
    return [(doc, score) for doc, score in ranked[:candidate_k]
            if float(score) >= threshold
            and float(semantic_scores.get(doc["id"], -1.0)) >= threshold]


def rerank_by_answer(ranked, semantic_scores, threshold=THRESHOLD, candidate_k=5):
    """C: rerank the original top candidates by query-to-answer cosine."""
    candidates = list(ranked[:candidate_k])
    return sorted(candidates,
                  key=lambda pair: float(semantic_scores.get(pair[0]["id"], -1.0)),
                  reverse=True)


_PROFILES = {
    "causal_pressure_glucose": {
        "terms": (("hypertension", "high blood pressure", "pression arterielle", "ضغط الدم"),
                  ("hyperglycemia", "hyperglycaemia", "high blood sugar", "elevated blood sugar",
                   "high blood glucose", "glycemie elevee", "hyperglycemie", "سكر الدم", "ارتفاع السكر")),
        "markers": ("cause", "because", "lead to", "result in", "result from", "due to",
                    "affect", "influence", "contribute to", "increase", "when",
                    "provoque", "causent", "entraine", "en raison de", "lie a", "يزيد", "يسبب", "تسبب"),
    },
    "compare_flu_dehydration": {
        "terms": (("flu", "influenza", "grippe", "انفلونزا"),
                  ("dehydration", "dehydrated", "deshydratation", "جفاف")),
        "markers": ("same", "similar", "differ", "compared", "versus", "unlike",
                    "identique", "similaire", "semblable", "difference", "comparison", "مقارنة"),
    },
    "compare_flu_cold": {
        "terms": (("flu", "influenza", "grippe"), ("common cold", "cold", "rhume")),
        "markers": ("different", "difference", "differ", "compared", "unlike", "overlap",
                    "similar", "same", "distinguish", "differentier", "similaire", "se distinguer"),
        "scope": "answer",
    },
    "association_diabetes_thirst": {
        "terms": (("diabetes", "diabetic", "diabete"), ("thirst", "thirsty", "soif")),
        "markers": ("symptom", "include", "including", "associated", "common sign", "can have"),
    },
    "causal_infection_fever": {
        "terms": (("infection", "infectious", "infection"), ("fever", "temperature", "feverish")),
        "markers": ("cause", "causes", "due to", "result from", "because", "responding to"),
    },
    "causal_illness_glucose": {
        "terms": (("illness", "illnesses", "disease", "infection"),
                  ("blood glucose", "blood sugar", "hyperglycemia", "glucose")),
        "markers": ("because of", "cause", "causes", "rise temporarily", "increase"),
    },
    "association_pressure_glucose": {
        "terms": (("hypertension", "high blood pressure", "pression arterielle", "ضغط الدم"),
                  ("hyperglycemia", "hyperglycaemia", "high blood sugar", "elevated blood sugar",
                   "high blood glucose", "glycemie elevee", "hyperglycemie", "سكر الدم", "ارتفاع السكر")),
        "markers": ("associated with", "linked to", "correlated with", "association between"),
    },
}


def _evidence_sentences(answer, profile):
    """Find answer sentences that co-express both concepts and a relation cue."""
    sentences = re.split(r"(?<=[.!?])\s+|[\n;]+", str(answer))
    evidence = []
    if profile.get("scope") == "answer":
        sentences = [" ".join(sentences)]
    for sentence in sentences:
        normalized = normalize(sentence)
        has_each_concept = all(
            any(normalize(alias) in normalized for alias in concept_group)
            for concept_group in profile["terms"]
        )
        markers = [normalize(marker) for marker in profile["markers"]
                   if normalize(marker) in normalized]
        if has_each_concept and markers:
            marker_position = min(normalized.find(marker) for marker in markers)
            before = normalized[max(0, marker_position - 36):marker_position]
            after = normalized[marker_position:marker_position + 44]
            if re.search(r"\b(not known|not clear|uncertain|unknown|insufficient evidence)\b", normalized):
                polarity = "uncertain"
            elif re.search(r"\b(no|not|never|cannot|does not|is not|without)\b", before) or re.search(
                r"\b(not|never|cannot)\b", after
            ):
                polarity = "denied"
            elif re.search(r"\b(may|might|can|could|often|sometimes|possible)\b", before):
                polarity = "qualified"
            else:
                polarity = "affirmed"
            evidence.append({"sentence": sentence.strip(), "polarity": polarity})
    return evidence


def explicitly_supports_relation(documents, relation_profile):
    profile = _PROFILES.get(relation_profile)
    return bool(profile) and any(
        _evidence_sentences(doc.get("answer", ""), profile) for doc in documents
    )


def explain_relation_decision(ranked, relation_profile, threshold=THRESHOLD):
    """Explain supported relation, partial context, rejection reason, and uncertainty."""
    candidates = [(doc, score) for doc, score in ranked[:5] if float(score) >= threshold]
    if not relation_profile:
        return {"documents": [doc for doc, _ in candidates], "partial_documents": [],
                "relation": None, "supporting_evidence": [],
                "reason": "no_relation_profile_requested", "uncertainty": "not_assessed"}
    profile = _PROFILES.get(relation_profile)
    if not profile:
        return {"documents": [], "partial_documents": [], "relation": relation_profile,
                "supporting_evidence": [], "reason": "unknown_relation_profile", "uncertainty": "high"}

    evidence = []
    partial_documents = []
    for doc, score in candidates:
        answer = doc.get("answer", "")
        sentences = _evidence_sentences(answer, profile)
        if sentences:
            evidence.append({"document_id": doc.get("id"), "sentences": sentences,
                             "retrieval_score": float(score)})
        normalized = normalize(answer)
        if any(any(normalize(alias) in normalized for alias in group) for group in profile["terms"]):
            partial_documents.append(doc)

    evidence_ids = {item["document_id"] for item in evidence}
    selected = [doc for doc, _ in candidates if doc.get("id") in evidence_ids]
    return {
        "documents": selected,
        "partial_documents": partial_documents if not selected else [],
        "relation": relation_profile,
        "supporting_evidence": evidence,
        "reason": "explicit_sentence_evidence" if selected else "no_single_sentence_supports_requested_relation",
        "uncertainty": "medium" if selected else "high",
    }


def relation_guard(ranked, relation_profile, threshold=THRESHOLD):
    """D gates relation answers while exposing relevant partial context separately."""
    if not relation_profile:
        return list(ranked)
    decision = explain_relation_decision(ranked, relation_profile, threshold)
    selected_ids = {doc.get("id") for doc in decision["documents"]}
    return [(doc, score) for doc, score in ranked[:5]
            if doc.get("id") in selected_ids and float(score) >= threshold]


def apply_method(method, ranked, semantic_scores=None, relation_profile=None,
                 threshold=THRESHOLD):
    semantic_scores = semantic_scores or {}
    if method == "A":
        return list(ranked)
    if method == "B":
        return answer_similarity_filter(ranked, semantic_scores, threshold)
    if method == "C":
        return rerank_by_answer(ranked, semantic_scores, threshold)
    if method == "D":
        return relation_guard(ranked, relation_profile, threshold)
    raise ValueError(f"Unknown method: {method}")
