
from pathlib import Path
import sys

# Permet d'importer le package app depuis le dossier backend.
BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.data.loader import load_data
from app.vectorstore.faiss_store import FAISSStore


DATA_PATH = (
    BACKEND_DIR
    / "data"
    / "data_enriched_v3_reviewed_copy.json"
)


def main():
    print("=== MediBot: test du dataset FAISS ===")
    print(f"Dataset : {DATA_PATH}")

    if not DATA_PATH.is_file():
        print("ERREUR : le fichier dataset est introuvable.")
        return 1

    # Étape 1 : chargement du JSON par le loader du projet.
    try:
        data = load_data(str(DATA_PATH))
    except Exception as exc:
        print(f"ERREUR pendant le chargement : {exc}")
        return 1

    print(f"Fiches chargées : {len(data)}")

    if len(data) != 37:
        print("ATTENTION : le nombre de fiches attendu est 37.")
        return 1

    # Étape 2 : construction du store FAISS en mémoire.
    try:
        store = FAISSStore(data)
    except Exception as exc:
        print(f"ERREUR pendant la création du store FAISS : {exc}")
        return 1

    print("Création du store FAISS : OK")
    print("Dataset original et main.py : non modifiés.")

    # Affiche les méthodes publiques pour préparer le test de recherche.
    public_methods = [
        name
        for name in dir(store)
        if not name.startswith("_")
        and callable(getattr(store, name, None))
    ]

    print("\nMéthodes publiques disponibles dans FAISSStore :")
    for method in public_methods:
        print(f" - {method}")

    print("\nTEST DE CHARGEMENT ET D'INITIALISATION : RÉUSSI")
    print(
        "Prochaine étape : utiliser la méthode de recherche réelle "
        "de FAISSStore pour tester des questions médicales."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
