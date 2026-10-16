import unittest
import sys
import json
from types import ModuleType
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
# Avoid loading/downloading the production sentence-transformer model just to
# import the agent during unit tests. Retrieval behavior is covered by StubStore.
embedding_stub = ModuleType("app.data.embedding")
embedding_stub.encode = lambda texts: None
sys.modules.setdefault("app.data.embedding", embedding_stub)

from app.agent import run_agent
from app.api import routes
from app.rag import rag_pipeline


class StubStore:
    def __init__(self, docs):
        self.docs = docs
        self.queries = []

    def search(self, query, k):
        self.queries.append(query)
        return [0.8] * len(self.docs), self.docs


class RagSourcesTests(unittest.IsolatedAsyncioTestCase):
    async def test_known_heart_attack_question_keeps_documents_without_sources(self):
        docs = [
            {"id": 31, "question": "What is a heart attack?", "answer": "A heart attack is an emergency."},
            {"id": 2, "question": "What should I do in case of chest pain?", "answer": "Seek emergency help."},
        ]
        store = StubStore(docs)
        with patch.object(rag_pipeline, "generate", new=AsyncMock(return_value="Appelez les urgences.")) as generate:
            result = await rag_pipeline.rag_answer("What is a heart attack?", store)

        self.assertEqual(result["answer"], "Appelez les urgences.")
        self.assertEqual(result["sources"], [])
        self.assertEqual(store.queries, ["What is a heart attack?"])
        prompt = generate.await_args.args[0]
        self.assertIn("What is a heart attack?", prompt)
        self.assertIn("A heart attack is an emergency.", prompt)
        self.assertIn("Seek emergency help.", prompt)
        self.assertIn("Answer entirely in English", prompt)
        self.assertNotIn("Réponds exclusivement en français", prompt)

    async def test_rag_uses_router_retrieval_without_searching_or_encoding_again(self):
        doc = {"id": 31, "question": "What is a heart attack?", "answer": "A heart attack is an emergency."}
        store = StubStore([doc])
        with patch.object(rag_pipeline, "generate", new=AsyncMock(return_value="Seek emergency help.")):
            result = await rag_pipeline.rag_answer(
                "What is a heart attack?", store, retrieval=([0.8], [doc])
            )
        self.assertIn("Seek emergency help", result["answer"])
        self.assertEqual(store.queries, [])

    async def test_valid_sources_are_returned_once_and_placeholders_rejected(self):
        docs = [
            {"question": "Q1", "answer": "A1", "source_name": "MedlinePlus", "source_url": "https://medlineplus.gov/heartattack.html"},
            {"question": "Q2", "answer": "A2", "source_name": "MedlinePlus", "source_url": "https://medlineplus.gov/heartattack.html"},
            {"question": "Q3", "answer": "A3", "source_name": "To be verified", "source_url": "https://example.org"},
            {"question": "Q4", "answer": "A4", "source_name": "CDC", "source_url": "javascript:alert(1)"},
        ]
        with patch.object(rag_pipeline, "generate", new=AsyncMock(return_value="Réponse")):
            result = await rag_pipeline.rag_answer("question", StubStore(docs))

        self.assertEqual(result["sources"], [{"name": "MedlinePlus", "url": "https://medlineplus.gov/heartattack.html"}])

    async def test_llm_timeout_and_error_use_localized_fallback_without_unverified_source_claim(self):
        docs = [{"question": "Q", "answer": "Réponse documentaire", "source_name": "NHS", "source_url": "https://www.nhs.uk/conditions/dehydration/"}]
        for error in (httpx.ReadTimeout("timeout"), RuntimeError("provider failed")):
            with self.subTest(error=type(error).__name__), patch.object(rag_pipeline, "generate", new=AsyncMock(side_effect=error)):
                result = await rag_pipeline.rag_answer("question", StubStore(docs))
                self.assertEqual(result, {
                    "answer": "I cannot generate a reliable answer right now. Please try again later.",
                    "sources": [],
                })

    async def test_heart_attack_dataset_sources_are_verified_references(self):
        dataset_path = Path(__file__).parents[1] / "data" / "data_enriched_v3.json"
        records = json.loads(dataset_path.read_text(encoding="utf-8"))
        by_id = {record["id"]: record for record in records}
        self.assertEqual(by_id[2]["source_name"], "NHS")
        self.assertEqual(by_id[2]["source_url"], "https://www.nhs.uk/symptoms/chest-pain/")
        self.assertEqual(by_id[31]["source_name"], "MedlinePlus")
        self.assertEqual(by_id[31]["source_url"], "https://medlineplus.gov/heartattack.html")
        self.assertIsNone(by_id[31]["reviewed_at"])

    async def test_agent_and_api_keep_sources_and_emergency_shape(self):
        with patch("app.agent.graph.ainvoke", new=AsyncMock(return_value={"response": {"answer": "RAG", "sources": [{"name": "NHS", "url": "https://www.nhs.uk/"}]}})):
            agent_result = await run_agent("question", object())
        self.assertEqual(agent_result["sources"][0]["name"], "NHS")

        with patch.object(routes, "run_agent", new=AsyncMock(return_value={"answer": "Urgence", "sources": []})):
            api_result = await routes.ask("chest pain")
        self.assertEqual(api_result, {"answer": "Urgence", "sources": []})

        with patch("app.agent.graph.ainvoke", new=AsyncMock(return_value={"response": "Urgence locale."})):
            emergency_result = await run_agent("chest pain", object())
        self.assertEqual(emergency_result, {"answer": "Urgence locale.", "sources": []})


if __name__ == "__main__":
    unittest.main()
