
from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.data.loader import load_data
from app.vectorstore.faiss_store import FAISSStore


DATA_PATH = BACKEND_DIR / "data" / "data_enriched_v3_reviewed_copy.json"

TEST_QUERIES = [
    {
        "question": "What are the symptoms of dehydration?",
        "expected_terms": ["dehydration", "dehydrated"],
    },
    {
        "question": "How can I prevent the flu?",
        "expected_terms": ["flu", "influenza"],
    },
    {
        "question": "What are the warning signs of a stroke?",
        "expected_terms": ["stroke"],
    },
    {
        "question": "Do antibiotics treat the common cold?",
        "expected_terms": ["antibiotic", "common cold", "cold"],
    },
    {
        "question": "What causes a fever?",
        "expected_terms": ["fever"],
    },
    {
        "question": "What should I do if I have chest pain?",
        "expected_terms": ["chest pain", "chest"],
    },
]


def main():
    print("=== MediBot : test de recherche FAISS ===")

    if not DATA_PATH.is_file():
        print(f"ERREUR : dataset introuvable : {DATA_PATH}")
        return 1

    data = load_data(str(DATA_PATH))
    print(f"Fiches chargées : {len(data)}")

    store = FAISSStore(data)
    print("Store FAISS initialisé.\n")

    for test in TEST_QUERIES:
        question = test["question"]
        expected_terms = test["expected_terms"]

        print("=" * 75)
        print(f"QUESTION : {question}")

        try:
            scores, documents = store.search(question, k=3)
        except Exception as exc:
            print(f"ERREUR de recherche : {exc}")
            continue

        if not documents:
            print("Aucun résultat.")
            continue

        for rank, (score, doc) in enumerate(
            zip(scores, documents), start=1
        ):
            doc_question = str(doc.get("question", ""))
            doc_answer = str(doc.get("answer", ""))
            doc_id = doc.get("id", "N/A")

            print(f"\n  Résultat {rank}")
            print(f"  ID         : {doc_id}")
            print(f"  Score      : {float(score):.4f}")
            print(f"  Question   : {doc_question}")
            print(f"  Réponse    : {doc_answer}")

        # Vérification indicative : au moins un résultat doit contenir
        # un terme associé au sujet. Ce n'est pas une mesure médicale
        # complète de la pertinence.
        top_text = " ".join(
            str(doc.get("question", "")) + " "
            + str(doc.get("answer", "")) + " "
            + " ".join(str(x) for x in doc.get("keywords", []))
            for doc in documents[:3]
        ).casefold()

        found = any(term in top_text for term in expected_terms)

        print(
            "\nContrôle lexical indicatif : "
            + ("SUJET REPÉRÉ" if found else "À EXAMINER")
        )

    print("\n=== Fin des tests ===")
    print("Ces résultats évaluent la recherche, pas l'exactitude médicale.")
    print("Aucun fichier de production n'a été modifié.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
