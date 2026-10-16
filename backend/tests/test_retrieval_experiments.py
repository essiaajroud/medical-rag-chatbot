from app.rag.retrieval_experiments import apply_strategy, source_identity


def doc(doc_id, language="en"):
    return {"id": doc_id, "_retrieved_language": language}


def test_language_filter_uses_target_results_and_does_not_mix_languages():
    rows = [(doc(37, "fr"), .8), (doc(0), .9), (doc(39, "ar"), .7)]
    selected = apply_strategy(rows, "B", "fr", .5)
    assert [item[0]["id"] for item in selected] == [37]


def test_language_filter_falls_back_to_english_only_when_target_below_threshold():
    rows = [(doc(37, "fr"), .49), (doc(0), .6)]
    selected = apply_strategy(rows, "B", "fr", .5)
    assert [item[0]["id"] for item in selected] == [0]


def test_dedup_keeps_highest_scoring_variant_per_source():
    rows = [(doc(0), .71), (doc(37, "fr"), .82), (doc(38, "ar"), .6)]
    selected = apply_strategy(rows, "C", "en", .5, candidate=True)
    assert len(selected) == 1
    assert selected[0][0]["id"] == 37
    assert source_identity(selected[0][0], candidate=True) == 0


def test_strategy_d_filters_then_deduplicates():
    rows = [(doc(37, "fr"), .8), (doc(0), .9), (doc(39, "ar"), .7)]
    selected = apply_strategy(rows, "D", "fr", .5)
    assert [item[0]["id"] for item in selected] == [37]

