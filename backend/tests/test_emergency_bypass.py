
import asyncio
from unittest.mock import AsyncMock, patch

from app.agent import run_agent


async def main():
    query = "I suddenly have weakness on one side of my body."

    # Le store ne doit pas être interrogé pour une urgence.
    store = AsyncMock()
    store.search.side_effect = AssertionError(
        "FAISS should not be called for an emergency."
    )

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
        assert result["answer"].strip(), "Emergency answer is empty."

        mock_rag.assert_not_awaited()
        mock_llm.assert_not_awaited()
        store.search.assert_not_called()

        print("PASS: emergency response returned.")
        print("PASS: RAG was not called.")
        print("PASS: LLM was not called.")
        print("PASS: FAISS search was not called.")
        print("Answer:", result["answer"])


if __name__ == "__main__":
    asyncio.run(main())
