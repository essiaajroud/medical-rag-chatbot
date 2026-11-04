
import json
import urllib.error
import urllib.request

API_URL = "http://127.0.0.1:8000/ask"

SCENARIOS = [
    {
        "name": "Déshydratation",
        "question": "What are the symptoms of dehydration?",
        "expected_keywords": ["thirst", "dry mouth", "urine"],
    },
    {
        "name": "Prévention de la grippe",
        "question": "How can I prevent the flu?",
        "expected_keywords": ["hand", "vaccine"],
    },
    {
        "name": "Urgence AVC",
        "question": (
            "What should I do if someone suddenly has facial "
            "drooping and difficulty speaking?"
        ),
        "expected_keywords": ["emergency", "immediately"],
    },
    {
        "name": "Douleur thoracique",
        "question": "What should I do if I have chest pain?",
        "expected_keywords": ["emergency", "immediately"],
    },
    {
        "name": "Antibiotiques et rhume",
        "question": "Do antibiotics treat the common cold?",
        "expected_keywords": ["virus", "viral", "antibiotics"],
    },
]


def ask_medibot(question):
    payload = json.dumps({
        "question": question,
        "history": [],
    }).encode("utf-8")

    request = urllib.request.Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def main():
    passed = 0

    for scenario in SCENARIOS:
        print("\n" + "=" * 65)
        print(f"TEST : {scenario['name']}")
        print(f"Question : {scenario['question']}")

        try:
            result = ask_medibot(scenario["question"])
            answer = result.get("answer", "")
            sources = result.get("sources", [])

            print(f"\nRéponse :\n{answer}")
            print(f"\nSources : {json.dumps(sources, ensure_ascii=False)}")

            normalized_answer = answer.lower()
            found = [
                keyword
                for keyword in scenario["expected_keywords"]
                if keyword.lower() in normalized_answer
            ]

            print(f"\nMots-clés trouvés : {found}")

            if answer.strip() and sources and found:
                print("RÉSULTAT TECHNIQUE : PASS")
                passed += 1
            else:
                print(
                    "RÉSULTAT TECHNIQUE : À EXAMINER "
                    "(réponse, mots-clés ou sources manquants)"
                )

        except urllib.error.HTTPError as error:
            print(f"ERREUR HTTP : {error.code}")
            print(error.read().decode("utf-8", errors="replace"))
        except Exception as error:
            print(f"ERREUR : {error}")

    print("\n" + "=" * 65)
    print(f"Résultat technique : {passed}/{len(SCENARIOS)}")
    print(
        "Attention : PASS vérifie seulement quelques critères techniques. "
        "Ce n'est pas une validation de la sécurité ou de l'exactitude médicale."
    )


if __name__ == "__main__":
    main()
