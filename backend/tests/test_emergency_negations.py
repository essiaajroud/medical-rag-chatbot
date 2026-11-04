
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.agent import detect_emergency_type


TESTS = [
    {
        "name": "Douleur thoracique niée",
        "query": "Je n'ai pas mal à la poitrine.",
        "expected": None,
    },
    {
        "name": "Difficulté respiratoire niée",
        "query": "Je n'ai pas de difficulté à respirer.",
        "expected": None,
    },
    {
        "name": "AVC : symptômes présents",
        "query": "Ma bouche est soudainement de travers et je parle difficilement.",
        "expected": "stroke",
    },
    {
        "name": "AVC malgré douleur thoracique niée",
        "query": "Je n'ai pas mal à la poitrine, mais ma bouche est soudainement de travers.",
        "expected": "stroke",
    },
    {
        "name": "Question informative sur l'AVC",
        "query": "Quels sont les signes d'un AVC ?",
        "expected": None,
    },
    {
        "name": "Question informative sur l'infarctus",
        "query": "What are the warning signs of a heart attack?",
        "expected": None,
    },
    {
        "name": "Douleur thoracique actuelle",
        "query": "J'ai une forte douleur à la poitrine en ce moment.",
        "expected": "cardiac",
    },
    {
        "name": "Difficulté respiratoire actuelle",
        "query": "Je n'arrive presque plus à respirer.",
        "expected": "breathing",
    },
]


def main():
    passed = 0

    for test in TESTS:
        actual = detect_emergency_type(test["query"])
        success = actual == test["expected"]

        print(f"\n{'OK' if success else 'ÉCHEC'} — {test['name']}")
        print(f"  Question : {test['query']}")
        print(f"  Attendu  : {test['expected']}")
        print(f"  Obtenu   : {actual}")

        if success:
            passed += 1

    print(f"\nRésultat : {passed}/{len(TESTS)} tests réussis.")

    if passed != len(TESTS):
        print(
            "Certaines règles doivent être ajustées. "
            "N'élargis pas les expressions régulières sans examiner "
            "les cas de négation et les questions informatives."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
