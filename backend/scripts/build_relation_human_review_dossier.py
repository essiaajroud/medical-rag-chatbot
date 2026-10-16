"""Build blinded human-review forms for experimental relation candidates only."""

import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.rag.relation_independent_protocol import (  # noqa: E402
    DEVELOPMENT_CANDIDATES,
    FINAL_CANDIDATES,
)

RAG_ROOT = BACKEND_ROOT / "app" / "rag"
PROVENANCE_PATH = RAG_ROOT / "relation_candidate_restorations.json"
CORPUS_PATH = BACKEND_ROOT / "data" / "data_enriched_v3.json"

# These are leads for the human corpus review, never gold evidence by themselves.
POSSIBLE_DOCS = {
    "d02": (32,), "d03": (5,), "d05": (4,), "d06": (36,),
    "i02": (36,), "i03": (36,), "i05": (4, 10), "i06": (4, 10),
    "i08": (35,), "i09": (35,), "i11": (1, 5), "i12": (1, 5),
    "i14": (), "i15": (), "i17": (),
}
UNCERTAINTIES = {
    "d02": "Association wording: confirm it asks whether thirst can accompany diabetes, without implying diagnosis or certainty.",
    "d03": "Arabic phrasing may read as symptoms changing relative to a cold rather than a natural comparison. Native Arabic adjudication required.",
    "d05": "Check the naturalness of the French wording and whether 'signes' is intended as symptoms/signs.",
    "d06": "Check Arabic wording for illness, blood sugar, and temporary duration; verify causal scope clinically.",
    "i02": "Check scope of 'prescribed medicine'; possible document 36 may speak only about certain medicines.",
    "i03": "Check Arabic equivalence for prescribed medicine and temporary effect.",
    "i05": "Causal dehydration–fatigue claim requires clinical review; separate mentions do not prove causality.",
    "i06": "Check Arabic modality and causal strength; clinical relation needs qualified review.",
    "i08": "The expected label says association, while candidate corpus wording may express causality; decide which relation is asked and what evidence qualifies.",
    "i09": "Check Arabic verb for association; distinguish association from causal direction.",
    "i11": "Check French COVID terminology and note corpus coverage may include flu but not COVID.",
    "i12": "Check Arabic disease names and comparison wording; do not infer a clinical comparison from flu-only documents.",
    "i14": "Anemia content may be outside the current corpus; any clinical answer requires an appropriate medical reviewer/source.",
    "i15": "Check Arabic terminology for anemia and clinical answer requirements; corpus may not cover it.",
    "i17": "No antecedent for 'them' is present in the candidate. Do not add context; decide whether to exclude or reformulate.",
}


def _load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _blank_review(case, provenance, docs, evaluator):
    return {
        "case_id": case["id"],
        "split": case["split"],
        "evaluator_code": "",
        "evaluator_id_if_process_allows": "",
        "review_date": "",
        "original_raw_corrupted": provenance["original_raw"],
        "original_unicode_repr": provenance["original_repr"],
        "proposed_restoration": provenance["proposed_text"],
        "language": case["language"],
        "expected_relation_type_from_candidate_design": case.get("candidate_relation_type"),
        "provenance": provenance["provenance"],
        "restoration_method": provenance["provenance"]["restoration_method"],
        "possible_corpus_documents_for_manual_inspection_only": docs,
        "question_understanding": "",
        "linguistic_review": {
            "grammar": "",
            "meaning_and_naturalness": "",
            "equivalent_to_raw_intended_text": "",
            "status": "needs_validation",
            "notes": "",
        },
        "medical_review": {
            "clinical_meaning_and_relation_direction": "",
            "evidence_level_required": "",
            "status": "needs_validation",
            "notes": "",
        },
        "intent": "",
        "relation_type_and_direction": "",
        "concepts_to_link": [],
        "evidence_level_required": "",
        "documents_relation_proving": [],
        "documents_partial_context": [],
        "documents_off_topic": [],
        "expected_answer": "",
        "justification": "",
        "decision": "",
        "decision_options": ["accepted", "to_correct", "ambiguous", "excluded"],
        "validation_status": "not_validated",
        "prediction_blinding_notice": "No A/D/E predictions or oracle profiles are included in this form.",
        "form_owner": evaluator,
    }


def build_review_bundle(provenance_path=PROVENANCE_PATH, corpus_path=CORPUS_PATH):
    provenance = {row["case_id"]: row for row in _load_json(provenance_path)["records"]}
    corpus = {row["id"]: row for row in _load_json(corpus_path)}
    candidates = {case["id"]: case for case in DEVELOPMENT_CANDIDATES + FINAL_CANDIDATES}
    if set(provenance) != set(POSSIBLE_DOCS):
        raise ValueError("Provenance IDs do not match the expected set of 15 review candidates")

    dossiers = []
    for case_id in POSSIBLE_DOCS:
        case = candidates[case_id]
        source_leads = [
            {
                "document_id": doc_id,
                "corpus_question_title": corpus[doc_id].get("question", ""),
                "status": "candidate_for_manual_content_check_not_evidence",
            }
            for doc_id in POSSIBLE_DOCS[case_id]
            if doc_id in corpus
        ]
        dossiers.append({
            "case_id": case_id,
            "split": case["split"],
            "raw_corrupted": provenance[case_id]["original_raw"],
            "unicode_escaped_repr": provenance[case_id]["original_repr"],
            "restored_proposal": provenance[case_id]["proposed_text"],
            "language": case["language"],
            "candidate_relation_type": case.get("candidate_relation_type"),
            "provenance": provenance[case_id]["provenance"],
            "reconstruction_method": provenance[case_id]["provenance"]["restoration_method"],
            "possible_documents_for_inspection_not_evidence": source_leads,
            "uncertainties": UNCERTAINTIES[case_id],
            "linguistic_validation": "needs_validation",
            "medical_validation": "needs_validation",
            "official_metrics_eligible": False,
        })

    evaluator_1 = {
        "packet_type": "blinded_independent_annotation",
        "evaluator_code": "reviewer_1",
        "instructions": "Complete independently. Do not seek or view A/D/E outputs. Document IDs are leads only; inspect document content before assigning proof status.",
        "forms": [_blank_review(candidates[d["case_id"]], provenance[d["case_id"]], d["possible_documents_for_inspection_not_evidence"], "reviewer_1") for d in dossiers],
    }
    evaluator_2 = {
        "packet_type": "blinded_independent_annotation",
        "evaluator_code": "reviewer_2",
        "instructions": "Complete independently. Do not seek or view A/D/E outputs. Document IDs are leads only; inspect document content before assigning proof status.",
        "forms": [_blank_review(candidates[d["case_id"]], provenance[d["case_id"]], d["possible_documents_for_inspection_not_evidence"], "reviewer_2") for d in dossiers],
    }
    adjudication = {
        "packet_type": "disagreement_adjudication",
        "instructions": "Open only after both independent forms are submitted and frozen. Do not consult A/D/E predictions. Do not fill a decision without an adjudicator.",
        "adjudicator_code": "",
        "adjudicator_id_if_process_allows": "",
        "date": "",
        "cases": [{
            "case_id": d["case_id"],
            "reviewer_1_decision_and_rationale": "",
            "reviewer_2_decision_and_rationale": "",
            "points_of_disagreement": [],
            "adjudicated_intent": "",
            "adjudicated_relation_type_and_direction": "",
            "adjudicated_evidence_level": "",
            "proof_document_ids": [],
            "partial_context_document_ids": [],
            "off_topic_document_ids": [],
            "expected_answer": "",
            "decision": "",
            "decision_options": ["accepted", "to_correct", "ambiguous", "excluded"],
            "justification_and_source_citations": "",
            "linguistic_validation": "needs_validation",
            "medical_validation": "needs_validation",
            "validation_status": "not_validated",
        } for d in dossiers],
    }
    return {"dossiers": dossiers, "evaluator_1": evaluator_1, "evaluator_2": evaluator_2, "adjudication": adjudication}


def _markdown(bundle):
    lines = [
        "# Dossier de revue humaine — candidats relationnels",
        "",
        "Paquet expérimental aveugle. Les documents listés sont des pistes de vérification, pas des preuves. Aucune prédiction A/D/E n'est fournie. Les décisions et validations sont laissées vides.",
        "",
        "## Procédure",
        "",
        "1. Distribuer séparément les fichiers `relation_review_evaluator_1.json` et `_2.json`; chaque évaluateur soumet et fige son fichier avant tout échange.",
        "2. Les évaluateurs vérifient compréhension, grammaire, sens, naturel et équivalence de la proposition avec le texte brut si récupérable. En l'absence d'original fiable, ils le notent au lieu de supposer l'équivalence.",
        "3. Inspecter le contenu des documents du corpus avant de les classer. Une ID ou un titre ne prouve aucune relation.",
        "4. Un tiers remplit `relation_review_adjudication.json` après réception des deux soumissions. Les désaccords et décisions restent traçables.",
        "5. Aucun statut ne devient validé automatiquement. Ne pas calculer de métrique officielle avec ces formulaires.",
        "",
        "## Fiches candidats",
    ]
    for d in bundle["dossiers"]:
        lines.extend([
            "", f"### {d['case_id']} — {d['language']} — split {d['split']}", "",
            f"- Brut corrompu : `{d['raw_corrupted']}`",
            f"- Représentation échappée : `{d['unicode_escaped_repr']}`",
            f"- Proposition : {d['restored_proposal']}",
            f"- Type de relation du candidat : `{d['candidate_relation_type']}`",
            f"- Provenance : {d['provenance']}",
            f"- Reconstruction : {d['reconstruction_method']}",
            "- Documents à examiner (non probants par défaut) : " + (
                "; ".join(f"{x['document_id']} — {x['corpus_question_title']}" for x in d["possible_documents_for_inspection_not_evidence"])
                if d["possible_documents_for_inspection_not_evidence"] else "aucun identifié"
            ),
            f"- Incertitudes : {d['uncertainties']}",
            "- Validation à remplir : compréhension; grammaire/naturalité/équivalence; intention/type; niveau de preuve; preuve, contexte partiel et hors sujet; réponse attendue; justification; décision; code/identité/date.",
            "- État actuel : linguistique `needs_validation`; médical `needs_validation`; métriques officielles exclues.",
        ])
    return "\n".join(lines) + "\n"


def write_review_bundle():
    bundle = build_review_bundle()
    outputs = {
        RAG_ROOT / "relation_human_review_dossier.md": _markdown(bundle),
        RAG_ROOT / "relation_review_evaluator_1.json": json.dumps(bundle["evaluator_1"], ensure_ascii=False, indent=2) + "\n",
        RAG_ROOT / "relation_review_evaluator_2.json": json.dumps(bundle["evaluator_2"], ensure_ascii=False, indent=2) + "\n",
        RAG_ROOT / "relation_review_adjudication.json": json.dumps(bundle["adjudication"], ensure_ascii=False, indent=2) + "\n",
    }
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8")
    return tuple(outputs)


if __name__ == "__main__":
    for output in write_review_bundle():
        print(output)
