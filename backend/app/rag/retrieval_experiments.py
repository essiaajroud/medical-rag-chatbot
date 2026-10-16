"""Offline retrieval strategies for the MediBot benchmark; never used in production."""


def source_identity(doc, candidate=False):
    """Candidate corpus appends French/Arabic variants in pairs per source ID."""
    doc_id = int(doc["id"])
    if candidate and doc_id >= 37:
        return (doc_id - 37) // 2
    return doc_id


def apply_strategy(ranked, strategy, language, threshold, candidate=True):
    """Return ranked (doc, score) rows for A/B/C/D, preserving the configured threshold."""
    rows = list(ranked)
    if strategy not in {"A", "B", "C", "D"}:
        raise ValueError(f"Unknown strategy: {strategy}")
    if strategy in {"A", "C"}:
        selected = rows
    else:
        target = [(doc, score) for doc, score in rows
                  if doc.get("_retrieved_language", "en") == language
                  and float(score) >= threshold]
        if target:
            selected = target
        else:
            selected = [(doc, score) for doc, score in rows
                        if doc.get("_retrieved_language", "en") == "en"
                        and float(score) >= threshold]
    if strategy in {"C", "D"}:
        best = {}
        for doc, score in selected:
            identity = source_identity(doc, candidate)
            if identity not in best or float(score) > float(best[identity][1]):
                best[identity] = (doc, score)
        selected = sorted(best.values(), key=lambda pair: -float(pair[1]))
    return selected
