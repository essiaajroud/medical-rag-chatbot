"""Human-readable, no-retrieval audit of the current experimental detector."""

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

BACKEND_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.rag.rejection_experiments import normalize
from app.rag.relation_generalization_benchmark import FINAL_CASES
from app.rag.relation_intent import (
    _CONCEPTS, _RELATION_MARKERS, _contains, detect_relation_intent,
)


def inspect_case(case):
    result = detect_relation_intent(case["question"])
    normalized = normalize(case["question"])
    matched_concepts = [
        name for name, aliases in _CONCEPTS.items()
        if any(_contains(normalized, alias) for alias in aliases)
    ]
    matched_types = [
        name for name, markers in _RELATION_MARKERS.items()
        if any(_contains(normalized, marker) for marker in markers)
    ]
    missing_concepts = sorted(set(case["concepts"]) - set(matched_concepts))
    expected_type = case["relation_type"]
    missing_type_cue = bool(expected_type and expected_type not in matched_types)
    return result, matched_concepts, matched_types, missing_concepts, missing_type_cue


def build_report():
    rows = []
    confusion = Counter()
    errors_by_language = defaultdict(list)
    for case in FINAL_CASES:
        result, matched_concepts, matched_types, missing_concepts, missing_type = inspect_case(case)
        predicted = result["intent"]
        expected = case["expected_intent"]
        confusion[(expected, predicted)] += 1
        if expected != predicted:
            if expected == "relation" and predicted in {"simple_information", "indeterminate"}:
                if case["relation_type"] == "comparison":
                    category = "comparison_missed"
                elif predicted == "indeterminate":
                    category = "relation_abstained"
                else:
                    category = "relation_missed_as_simple"
            elif expected == "simple_information" and predicted == "relation":
                category = "simple_false_relation"
            elif expected == "indeterminate":
                category = "indeterminate_misclassified"
            else:
                category = "other_intent_error"
            details = []
            if missing_concepts:
                details.append("concept aliases not matched: " + ", ".join(missing_concepts))
            if missing_type:
                details.append("no marker matched for expected type " + str(case["relation_type"]))
            if not details:
                details.append("rule precedence or profile inventory produced this label")
            row = {
                "case": case, "result": result, "category": category,
                "matched_concepts": matched_concepts, "matched_relation_types": matched_types,
                "explanation": "; ".join(details),
            }
            rows.append(row)
            errors_by_language[case["language"]].append(row)

    lines = [
        "# Audit des erreurs du détecteur relationnel E",
        "",
        "Audit calculé sur les 27 questions finales existantes, avec les règles actuelles non modifiées. "
        "Les annotations de référence n’ont pas été changées.",
        "",
        "## Matrice de confusion",
        "",
        "Lignes = intention attendue; colonnes = intention prédite.",
        "",
        "| Attendue \\ Prédite | relation | information simple | indéterminée | Total |",
        "|---|---:|---:|---:|---:|",
    ]
    labels = ("relation", "simple_information", "indeterminate")
    for actual in labels:
        cells = [confusion[(actual, predicted)] for predicted in labels]
        lines.append(f"| {actual} | {cells[0]} | {cells[1]} | {cells[2]} | {sum(cells)} |")
    lines.extend(["", "## Erreurs par langue", "", "| Langue | Erreurs / cas | Relations manquées comme simples | Relations indéterminées | Comparaisons manquées | Simples faussement relationnelles |", "|---|---:|---:|---:|---:|---:|"])
    for lang in ("en", "fr", "ar"):
        cases = [case for case in FINAL_CASES if case["language"] == lang]
        errors = errors_by_language[lang]
        counts = Counter(row["category"] for row in errors)
        lines.append(
            f"| {lang.upper()} | {len(errors)} / {len(cases)} | {counts['relation_missed_as_simple']} | "
            f"{counts['relation_abstained']} | {counts['comparison_missed']} | {counts['simple_false_relation']} |"
        )
    lines.extend(["", "## Détail des erreurs", ""])
    if not rows:
        lines.append("Aucune erreur.")
    for row in rows:
        case, result = row["case"], row["result"]
        lines.extend([
            f"### {case['id']} ({case['language'].upper()}) — {row['category']}",
            f"- Question : {case['question']}",
            f"- Attendu : `{case['expected_intent']}`; prédit : `{result['intent']}` "
            f"(type={result['relation_type']}, profil={result['profile']}, confiance={result['confidence']:.2f}).",
            f"- Relation/catégorie annotée : `{case['relation_type'] or 'aucune'}` / `{case['evidence_level']}`.",
            f"- Vérification : {row['explanation']}; détections observées : concepts="
            f"{row['matched_concepts']}, types={row['matched_relation_types']}.",
            "",
        ])
    lines.extend([
        "## Cas f10 : annotation ambiguë à conserver et comparer séparément",
        "",
        "L’annotation originale reste `relation/association`, profil `association_diabetes_thirst`, preuve explicite, document 32. "
        "La formulation anglaise « can cause » autorise aussi une lecture causale; la fiche 32 décrit la soif comme symptôme possible, "
        "ce qui n’établit pas à elle seule un mécanisme causal.",
        "",
        "Une annotation alternative raisonnable est `relation/causal`, avec `preuve suffisante = non établie par le corpus`, "
        "document 32 comme contexte partiel uniquement et réponse attendue : ne pas affirmer la causalité; signaler la limite des sources. "
        "Cette annotation ne signifie pas que la causalité est médicalement fausse. Sa validation nécessite une source clinique fiable établissant "
        "le lien, son sens et ses conditions (par exemple hyperglycémie/polydipsie), puis une revue par une personne qualifiée.",
        "",
        "Le détecteur retourne `indeterminate` pour f10 car le marqueur causal produit un type sans profil diabetes-thirst correspondant. "
        "Cela constitue un désaccord entre l’annotation actuelle et la taxonomie du détecteur, pas une preuve pour l’une ou l’autre annotation.",
        "",
        "## Portée",
        "",
        "Le benchmark final actuel est petit, composé pendant le même travail que le détecteur et réutilise les concepts/profils de la base et "
        "du benchmark historique. Ses questions sont lexicalement distinctes du développement, mais le jeu n’a pas été aveugle. "
        "Les chiffres arabes portent sur des phrases Unicode valides; la console Windows peut afficher ces caractères de façon trompeuse.",
        "",
    ])
    return "\n".join(lines), rows, confusion


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, help="Write the audit Markdown to this path")
    args = parser.parse_args()
    report, _, _ = build_report()
    if args.output:
        args.output.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
