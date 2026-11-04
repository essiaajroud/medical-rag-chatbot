from app.agent import detect_emergency_type, _normalize

tests = {
    "وجهي يتدلّى وأجد صعوبة مفاجئة في الكلام": "stroke",
    "اعوجاج مفاجئ في الوجه وثقل في اللسان": "stroke",
    "أعاني من ألم شديد في الصدر": "cardiac",
    "لا أستطيع التنفس": "breathing",
    "I suddenly cannot speak clearly.": "stroke",
    "J’ai une forte oppression dans la poitrine.": "cardiac",
    "عندي ضيق شديد في التنفس": "breathing",

}

for query, expected in tests.items():
    actual = detect_emergency_type(query)
    status = "PASS" if actual == expected else "FAIL"

    print(f"[{status}] {query}")
    print(f"  Expected: {expected}")
    print(f"  Actual:   {actual}")


stroke_cases = [
    "I suddenly have weakness on one side of my body.",
    "Sudden weakness on one side of the body.",
    "I have numbness on the left side of my body.",
    "I suddenly cannot speak clearly.",
    "What should I do if someone suddenly has facial drooping?",
    "أعاني من ضعف مفاجئ في أحد جانبي جسمي"
]

for query in stroke_cases:
    result = detect_emergency_type(query)
    print(f"{'PASS' if result == 'stroke' else 'FAIL'} | {query} -> {result}")
    print("Original :", repr(query))
    print("Normalized :", repr(_normalize(query)))
    print("Detected :", repr(detect_emergency_type(query)))
    assert result == "stroke", f"Expected stroke detection for: {query}"


from app.agent import detect_emergency_type


testss = [
    # =========================
    # STROKE / AVC / السكتة الدماغية
    # =========================
    ("I suddenly have weakness on one side of my body.", "stroke"),
    ("Sudden weakness on one side of the body.", "stroke"),
    ("I have numbness on the left side of my body.", "stroke"),
    ("I suddenly cannot speak clearly.", "stroke"),
    ("What should I do if someone suddenly has facial drooping?", "stroke"),
    ("J’ai soudainement une faiblesse d’un côté du corps.", "stroke"),
    ("Une personne présente soudainement un trouble de la parole.", "stroke"),
    ("أعاني من ضعف مفاجئ في أحد جانبي جسمي", "stroke"),
    ("اعوجاج مفاجئ في الوجه وثقل في اللسان", "stroke"),
    ("وجهي يتدلّى وأجد صعوبة مفاجئة في الكلام", "stroke"),

    # =========================
    # CARDIAC / DOULEUR THORACIQUE / ألم الصدر
    # =========================
    ("I have severe chest pain.", "cardiac"),
    ("I feel crushing pressure in my chest.", "cardiac"),
    ("J’ai une forte oppression dans la poitrine.", "cardiac"),
    ("J’ai une douleur thoracique intense.", "cardiac"),
    ("أعاني من ألم شديد في الصدر", "cardiac"),

    # =========================
    # BREATHING / RESPIRATION / التنفس
    # =========================
    ("I cannot breathe.", "breathing"),
    ("I am struggling to breathe.", "breathing"),
    ("J’ai beaucoup de mal à respirer.", "breathing"),
    ("Je n’arrive plus à respirer.", "breathing"),
    ("لا أستطيع التنفس", "breathing"),
    ("عندي ضيق شديد في التنفس", "breathing"),

    # =========================
    # UNCONSCIOUSNESS / PERTE DE CONNAISSANCE
    # Vérifie les noms de catégories configurés dans agent.py.
    # =========================
    ("The person is unconscious and won't wake up.", "unconsciousness"),
    ("La personne est inconsciente et ne se réveille pas.", "unconsciousness"),
]


failed = 0

for query, expected in testss:
    actual = detect_emergency_type(query)
    passed = actual == expected

    print(
        f"[{'PASS' if passed else 'FAIL'}] {query}\n"
        f"  Expected: {expected}\n"
        f"  Actual:   {actual}"
    )

    if not passed:
        failed += 1

print(f"\nResults: {len(testss) - failed}/{len(testss)} passed")

if failed:
    raise SystemExit(1)



negative_tests = [
    "What are the signs of a stroke?",
    "What is the difference between a cold and the flu?",
    "What causes a mild headache?",
    "Quels sont les symptômes d’un AVC ?",
    "ما هي أعراض السكتة الدماغية؟",
]

for query in negative_tests:
    actual = detect_emergency_type(query)
    passed = actual is None

    print(
        f"[{'PASS' if passed else 'FAIL'}] "
        f"{query} -> {actual}"
    )
