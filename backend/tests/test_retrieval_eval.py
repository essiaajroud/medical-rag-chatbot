import unittest

from scripts.rag_eval import calculate_metrics


class RetrievalEvaluationTests(unittest.TestCase):
    def test_metrics_use_document_annotations_and_threshold_for_no_answer(self):
        cases = [
            {"query": "q-en", "language": "en", "relevant_ids": {1, 2}},
            {"query": "q-fr", "language": "fr", "relevant_ids": {3}},
            {"query": "q-none", "language": "en", "relevant_ids": set()},
        ]
        results = {
            "q-en": ([{"id": 2}, {"id": 9}], [0.9, 0.8]),
            "q-fr": ([{"id": 3}, {"id": 4}], [0.7, 0.4]),
            "q-none": ([{"id": 8}], [0.2]),
        }
        metrics = calculate_metrics(cases, results, k=2, threshold=0.5)
        self.assertEqual(metrics["recall_at_k"], 0.75)
        self.assertEqual(metrics["precision_at_k"], 0.5)
        self.assertEqual(metrics["mrr"], 1.0)
        self.assertEqual(metrics["no_relevant_document_rate"], 0.0)
        self.assertEqual(metrics["recall_by_language"], {"en": 0.5, "fr": 1.0})

    def test_duplicate_language_variants_do_not_inflate_recall(self):
        cases = [{"query": "q", "language": "fr", "relevant_ids": {35}}]
        results = {"q": ([{"id": 35}, {"id": 35}], [0.9, 0.8])}
        metrics = calculate_metrics(cases, results, k=2, threshold=0.5)
        self.assertEqual(metrics["recall_at_k"], 1.0)
        self.assertEqual(metrics["precision_at_k"], 0.5)


if __name__ == "__main__":
    unittest.main()
