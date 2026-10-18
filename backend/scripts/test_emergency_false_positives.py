
"""
Tests des faux positifs et des cas limites de MediBot.

À exécuter depuis le dossier backend :
python -m scripts.test_emergency_false_positives
"""

from app.agent import detect_emergency_type


# Cas qui ne devraient pas déclencher une alerte automatique.
NEGATIVE_CASES = [
    # Questions informatives générales
    ("What are the signs of a stroke?", None),
    ("What is the difference between a cold and the flu?", None),
    ("Quels sont les symptômes d’un AVC ?", None),
    ("ما هي أعراض السكتة الدماغية؟", None),

    # Symptômes courants sans signe d'urgence explicite
    ("I have a mild headache after a long day.", None),
    ("J’ai un léger mal de gorge depuis ce matin.", None),
    ("I feel tired after exercising.", None),

    # Informations générales ou hypothétiques
    ("Can a stroke cause speech problems?", None),
    ("Quels sont les facteurs de risque de l’AVC ?", None),
    ("How can I prevent respiratory infections?", None),
]

False_NEGATIVE_CASES = [
    ("My face suddenly looks uneven.", "stroke"),
    ("I suddenly can’t get my words out.", "stroke"),
    ("Someone is gasping for air.", "breathing"),
    ("He collapsed and won’t wake up.", "unconsciousness"),
    ("I have severe chest pain spreading to my arm.", "cardiac"),
]

# Cas qui doivent continuer à déclencher une alerte.
POSITIVE_CASES = [
    (
        "I suddenly have weakness on one side of my body.",
        "stroke",
    ),
    (
        "J’ai soudainement une faiblesse d’un côté du corps.",
        "stroke",
    ),
    (
        "أعاني من ضعف مفاجئ في أحد جانبي جسمي",
        "stroke",
    ),
    (
        "I have crushing chest pressure right now.",
        "cardiac",
    ),
    (
        "I cannot breathe properly right now.",
        "breathing",
    ),
]

LIMITE_CASES = [
    ("My father suddenly cannot speak.", "stroke"),
    ("I suddenly feel weak on one side, but it is getting better.", "stroke"),
    ("I don't have chest pain or breathing problems.", None),
    ("Can sudden weakness be a sign of a stroke?", None),
    ("I don't have chest pain, but I can barely breathe.", "breathing"),
]

MANUAL_REVIEW_CASES = [
    "I had chest pain yesterday, but I feel fine now.",
]


def run_cases(title, cases):
    print(f"\n--- {title} ---")
    passed = 0

    for message, expected in cases:
        actual = detect_emergency_type(message)
        ok = actual == expected

        if ok:
            passed += 1
            status = "PASS"
        else:
            status = "FAIL"

        print(
            f"[{status}] {message!r}\n"
            f"       Expected: {expected!r} | Actual: {actual!r}"
        )

    print(f"Résultat : {passed}/{len(cases)} réussis")
    return passed, len(cases)


def main():
    neg_passed, neg_total = run_cases(
        "FAUX POSITIFS — aucune alerte attendue",
        NEGATIVE_CASES,
    )

    pos_passed, pos_total = run_cases(
        "CONTRÔLE — urgences toujours détectées",
        POSITIVE_CASES,
    )

    lim_passed, lim_total = run_cases(
            "CAS LIMITES — situations ambigües",
            LIMITE_CASES,
        )

    FN_passed, FN_total = run_cases(
                "FAUX NÉGATIFS — urgences manquées",
                False_NEGATIVE_CASES,
            )

    total_passed = neg_passed + pos_passed + lim_passed + FN_passed
    total = neg_total + pos_total + lim_total + FN_total

    print(f"\nTOTAL : {total_passed}/{total} réussis")

    if total_passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
