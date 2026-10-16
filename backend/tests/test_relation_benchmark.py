from app.rag.relation_benchmark import CASES


def test_benchmark_has_manual_content_annotations_across_all_target_languages():
    assert {case["lang"] for case in CASES} == {"en", "fr", "ar"}
    assert len(CASES) >= 40
    for case in CASES:
        assert case["claims"]
        assert "corpus_sufficient" in case
        assert case["expected_behavior"]
        if case["gold"] is not None:
            assert all(0 <= source_id <= 36 for source_id in case["gold"])


def test_benchmark_contains_supported_and_unsupported_relations_and_emergency_route():
    assert any(case.get("relation") == "compare_flu_cold" and case["gold"] for case in CASES)
    assert any(case.get("relation") == "causal_pressure_glucose" and not case["gold"] for case in CASES)
    assert any(case.get("route") == "emergency" for case in CASES)
