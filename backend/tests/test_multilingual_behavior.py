import sys
import unittest
from types import ModuleType
from unittest.mock import AsyncMock, patch

embedding_stub = ModuleType("app.data.embedding")
embedding_stub.encode = lambda texts: None
sys.modules.setdefault("app.data.embedding", embedding_stub)

from app.agent import classify_question, detect_emergency_type
from app.api import routes
from app.core.language_utils import detect_language, get_greeting
from app.rag import rag_pipeline


class MultilingualBehaviorTests(unittest.IsolatedAsyncioTestCase):
    def test_language_and_medical_routing(self):
        cases = {
            "What are the signs of high blood sugar?": ("en", "medical"),
            "Quels sont les signes d’une glycémie élevée ?": ("fr", "medical"),
            "ما هي أعراض ارتفاع السكر في الدم؟": ("ar", "medical"),
            "What is hyperglycemia?": ("en", "medical"),
            "Does high blood sugar always mean diabetes?": ("en", "medical"),
        }
        for query, expected in cases.items():
            with self.subTest(query=query):
                self.assertEqual((detect_language(query), classify_question(query)), expected)
        self.assertEqual(classify_question("How do I create a Python class?"), "out_of_scope")

    async def test_greetings_return_exact_localized_text_without_agent_or_store(self):
        cases = {
            "Bonjour": "Bonjour 👋 Je suis MediBot. Comment puis-je vous aider aujourd'hui ?",
            "Hello!": "Hello 👋 I'm MediBot. How can I help you today?",
            "مرحبا": "مرحبًا 👋 أنا MediBot. كيف يمكنني مساعدتك اليوم؟",
        }
        for query, expected in cases.items():
            with self.subTest(query=query), patch.object(routes, "run_agent", new=AsyncMock()) as run:
                routes.store_instance = object()
                self.assertEqual(await routes.ask(query), {"answer": expected, "sources": []})
                run.assert_not_awaited()
        self.assertIsNone(get_greeting("Hello, what is diabetes?"))

    
    async def test_rag_without_context_returns_localized_fallback_without_sources(self):
        store = type("Store", (), {
            "search": lambda self, query, k: ([], [])
        })()

        with patch.object(
            rag_pipeline,
            "generate",
            new=AsyncMock(return_value="La réponse")
        ) as generate:
            result = await rag_pipeline.rag_answer(
                "Quels sont les signes du diabète ?",
                store
            )

        self.assertIn(
            "Je n’ai pas trouvé suffisamment d’informations",
            result["answer"]
        )
        self.assertEqual(result["sources"], [])
        generate.assert_not_awaited()


    async def test_emergency_priority(self):
        self.assertEqual(detect_emergency_type("I have chest pain and difficulty breathing."), "cardiac")
        self.assertEqual(classify_question("I have chest pain and difficulty breathing."), "emergency")


if __name__ == "__main__":
    unittest.main()
