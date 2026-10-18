
import asyncio
from unittest.mock import AsyncMock, Mock, patch

from app.agent import detect_emergency_type, run_agent


CASES = [
    # AVC
    ("I suddenly have weakness on one side of my body.", "stroke"),
    ("J’ai soudainement une faiblesse d’un côté du corps.", "stroke"),
    ("أعاني من ضعف مفاجئ في أحد جانبي جسمي", "stroke"),

    # Urgence cardiaque
    ("I have crushing chest pressure right now.", "cardiac"),
    ("J’ai une forte oppression dans la poitrine.", "cardiac"),

    # Difficultés respiratoires
    ("I cannot breathe properly right now.", "breathing"),
    ("I can barely breathe.", "breathing"),

    # Perte de connaissance
    ("The person is unconscious and unresponsive.", "unconsciousness"),
]


async def run_case(query: str, expected_type: str) -> bool:
    store = Mock()
    store.search.side_effect = AssertionError(
        "FAISS must not be called for an emergency."
    )

    try:
        # Vérifie d'abord la catégorie détectée.
        actual_type = detect_emergency_type(query)

        assert actual_type == expected_type, (
            f"Expected emergency type {expected_type!r}, "
            f"got {actual_type!r}"
        )

        # Vérifie ensuite le contournement du RAG, du LLM et de FAISS.
        with (
            patch(
                "app.agent.rag_answer",
                new_callable=AsyncMock,
            ) as mock_rag,
            patch(
                "app.agent.general_answer",
                new_callable=AsyncMock,
            ) as mock_llm,
        ):
            result = await run_agent(query, store)

            assert isinstance(result["answer"], str)
            assert result["answer"].strip()

            mock_rag.assert_not_awaited()
            mock_llm.assert_not_awaited()
            store.search.assert_not_called()

        print(f"[PASS] {expected_type}: {query}")
        return True

    except Exception as exc:
        print(f"[FAIL] {expected_type}: {query}")
        print(f"       {type(exc).__name__}: {exc}")
        return False


async def main():
    passed = 0

    for query, expected_type in CASES:
        if await run_case(query, expected_type):
            passed += 1

    print(f"\nTOTAL: {passed}/{len(CASES)} tests passed")

    if passed != len(CASES):
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
