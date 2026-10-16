import sys
import unittest
from types import ModuleType
from unittest.mock import AsyncMock, patch

# The production embedding module may download a model on import. These tests
# exercise intent routing and use a small in-memory store instead.
embedding_stub = ModuleType("app.data.embedding")
embedding_stub.encode = lambda texts: None
sys.modules.setdefault("app.data.embedding", embedding_stub)

from app.agent import classify_question, detect_emergency_type, run_agent


class StubStore:
    def __init__(self, distances=None, docs=None):
        self.distances = distances if distances is not None else [1.5]
        self.docs = docs if docs is not None else []
        self.queries = []

    def search(self, query, k=None):
        self.queries.append(query)
        return self.distances, self.docs


class AgentRoutingTests(unittest.IsolatedAsyncioTestCase):
    def test_emergencies_are_detected_in_english_and_french(self):
        cases = {
            "I have severe chest pain": "cardiac",
            "I can't breathe": "breathing",
            "Her face is drooping and she can't speak clearly": "stroke",
            "My father is unconscious": "unconsciousness",
            "Que dois-je faire si j’ai une douleur thoracique ?": "cardiac",
            "Je n'arrive pas à respirer": "breathing",
            "Son visage s'affaisse soudainement et elle a du mal à parler": "stroke",
            "Il a perdu connaissance": "unconsciousness",
        }
        for query, expected in cases.items():
            with self.subTest(query=query):
                self.assertEqual(detect_emergency_type(query), expected)
                self.assertEqual(classify_question(query), "emergency")

    def test_educational_disease_questions_are_medical_not_active_emergencies(self):
        for query in (
            "What is a heart attack?", "What is a stroke?", "Qu’est-ce qu’un AVC ?",
            "J’ai mal à la gorge depuis hier.",
        ):
            with self.subTest(query=query):
                self.assertEqual(classify_question(query), "medical")

    def test_unseen_disease_and_ambiguous_short_question_are_handled_as_medical_or_unclear(self):
        self.assertEqual(classify_question("What are the symptoms of lupus?"), "medical")
        self.assertEqual(classify_question("Is it bad?"), "unclear")

    async def test_emergency_bypasses_retrieval_and_returns_specific_response(self):
        for query, expected in (
            ("What should I do about chest pain?", "Chest pain"),
            ("Que dois-je faire si j’ai une douleur thoracique ?", "douleur thoracique"),
            ("J’ai une douleur thoracique, que faire ?", "douleur thoracique"),
            ("My face is drooping", "stroke"),
        ):
            store = StubStore()
            with self.subTest(query=query):
                result = await run_agent(query, store)
                self.assertIn(expected, result["answer"])
                self.assertEqual(result["sources"], [])
                self.assertEqual(store.queries, [])

    async def test_emergency_variants_never_call_rag_or_llm(self):
        from app.rag import rag_pipeline

        queries = (
            "I have severe chest pain and difficulty breathing.",
            "J’ai une douleur thoracique intense.",
            "La personne est inconsciente et ne respire pas normalement.",
        )
        with patch("app.agent.rag_answer", new=AsyncMock()) as rag, patch.object(
            rag_pipeline, "generate", new=AsyncMock()
        ) as llm:
            results = [await run_agent(query, StubStore()) for query in queries]
        rag.assert_not_awaited()
        llm.assert_not_awaited()
        self.assertTrue(all("emergency" in result["answer"].lower() or "urgence" in result["answer"].lower() for result in results))
        self.assertIn("réanimation", results[2]["answer"].lower())
        self.assertIn("haut-parleur", results[2]["answer"].lower())
        self.assertTrue(all(result["sources"] == [] for result in results))

    async def test_relevant_sore_throat_questions_use_rag(self):
        from app.rag import rag_pipeline

        queries = (
            "J’ai mal à la gorge depuis hier, chnowa naamel ?",
            "J’ai mal à la gorge depuis hier.",
            "I have a mild sore throat but no fever.",
        )
        for query in queries:
            store = StubStore(distances=[1.15], docs=[{"question": "sore throat", "answer": "Sore throat information."}])
            rag_result = {"answer": "Please rest, drink fluids, and seek care if breathing becomes difficult. This is not a diagnosis.", "sources": []}
            with self.subTest(query=query), patch("app.agent.rag_answer", new=AsyncMock(return_value=rag_result)) as rag, patch.object(
                rag_pipeline, "generate", new=AsyncMock()
            ) as llm:
                result = await run_agent(query, store)
                self.assertEqual(store.queries, [query])
                rag.assert_awaited_once()
                self.assertEqual(rag.await_args.args, (query, store))
                self.assertEqual(rag.await_args.kwargs["retrieval"], ([1.15], store.docs))
                llm.assert_not_awaited()
            self.assertIn("drink fluids", result["answer"])
            self.assertIn("breathing", result["answer"])
            self.assertIn("diagnosis", result["answer"])
            self.assertEqual(result["sources"], [])

    async def test_source_request_is_honest_without_conversation_context(self):
        from app.rag import rag_pipeline

        query = "Give me the sources for your answer about heart attacks."
        store = StubStore()
        with patch("app.agent.rag_answer", new=AsyncMock()) as rag, patch.object(
            rag_pipeline, "generate", new=AsyncMock()
        ) as llm:
            result = await run_agent(query, store)
        self.assertIn("do not have access", result["answer"])
        self.assertIn("original medical question", result["answer"])
        self.assertEqual(result["sources"], [])
        self.assertEqual(store.queries, [])
        rag.assert_not_awaited()
        llm.assert_not_awaited()

    async def test_medical_question_without_reliable_match_gets_cautious_answer(self):
        store = StubStore(distances=[1.2])
        with patch("app.agent.general_answer", new=AsyncMock(return_value="I can provide general information, not a diagnosis.")):
            result = await run_agent("What is sepsis?", store)
        self.assertIn("diagnosis", result["answer"])
        self.assertEqual(result["sources"], [])
        self.assertEqual(store.queries, ["What is sepsis?"])

    async def test_unseen_medical_question_uses_general_fallback_without_sources(self):
        store = StubStore(distances=[0.2], docs=[{"id": 10, "question": "Fatigue", "answer": "General information."}])
        answer = "Lupus is a complex condition. This is general information, not a diagnosis."
        with patch("app.agent.general_answer", new=AsyncMock(return_value=answer)) as general:
            result = await run_agent("What are the symptoms of lupus?", store)
        self.assertEqual(result, {"answer": answer, "sources": []})
        self.assertEqual(store.queries, ["What are the symptoms of lupus?"])
        general.assert_awaited_once()

    async def test_relevant_medical_question_uses_rag_when_within_threshold(self):
        store = StubStore(distances=[0.8], docs=[{"question": "What is fever?", "answer": "A raised temperature."}])
        rag_result = {"answer": "Une fièvre est une température élevée.", "sources": []}
        with patch("app.agent.rag_answer", new=AsyncMock(return_value=rag_result)) as rag:
            result = await run_agent("What causes a fever?", store)
        self.assertEqual(result, rag_result)
        rag.assert_awaited_once_with(
            "What causes a fever?", store,
            retrieval=([0.8], [{"question": "What is fever?", "answer": "A raised temperature."}]),
        )
        self.assertEqual(store.queries, ["What causes a fever?"])

    async def test_clear_out_of_scope_questions_are_refused_without_retrieval(self):
        for query in ("Tell me about the Roman Empire", "Write a Python program"):
            store = StubStore()
            with self.subTest(query=query):
                self.assertEqual(classify_question(query), "out_of_scope")
                result = await run_agent(query, store)
                self.assertIn("medical information assistant", result["answer"])
                self.assertEqual(store.queries, [])
                self.assertEqual(result["sources"], [])

    async def test_unintelligible_message_requests_rephrasing(self):
        for query in ("asdf qwer zxcv", "asdfghjkl 12345"):
            store = StubStore()
            with self.subTest(query=query):
                self.assertEqual(classify_question(query), "unclear")
                result = await run_agent(query, store)
                self.assertIn("rephrase", result["answer"])
                self.assertEqual(store.queries, [])


if __name__ == "__main__":
    unittest.main()
