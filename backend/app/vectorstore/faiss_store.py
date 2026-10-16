import faiss
from app.data.embedding import encode
import numpy as np

class FAISSStore:
    def __init__(self, data):
        if not data:
            raise ValueError("La base médicale est vide.")

        self.data = data

        texts = []
        for doc in data:
            keywords = doc.get("keywords", [])
            related = doc.get("related_questions", [])

            if not isinstance(keywords, list):
                keywords = []
            if not isinstance(related, list):
                related = []

            text = " ".join([
                str(doc.get("question", "")),
                str(doc.get("answer", "")),
                " ".join(str(x) for x in keywords),
                " ".join(str(x) for x in related),
                str(doc.get("category", "")),
            ])
            texts.append(text)

        self.embeddings = encode(texts).astype(np.float32)

        # Produit scalaire = similarité cosinus
        # si les vecteurs sont normalisés.
        self.index = faiss.IndexFlatIP(
            self.embeddings.shape[1]
        )
        self.index.add(self.embeddings)

    
    def _topic_queries(self, query):
        """Create focused queries for supported medical topics."""
        q = query.casefold()

        topics = {
            "dehydration": {
                "aliases": [
                    "dehydration", "dehydrated",
                    "الجفاف", "جفاف", "نقص السوائل",
                ],
                "query": (
                    "What are the symptoms of dehydration? "
                    "Dizziness, lightheadedness, thirst, "
                    "dry mouth, reduced urination."
                ),
            },
            "diabetes": {
                "aliases": [
                    "diabetes", "diabetic", "blood sugar",
                    "السكري", "مرض السكري", "داء السكري",
                    "ارتفاع السكر",
                ],
                "query": (
                    "What are the common symptoms of diabetes? "
                    "Increased thirst, frequent urination, "
                    "hunger, fatigue, blurred vision."
                ),
            },
            "dizziness": {
                "aliases": [
                    "dizziness", "dizzy", "lightheadedness",
                    "الدوخة", "دوخة", "الدوار",
                ],
                "query": (
                    "What medical conditions can cause dizziness "
                    "or lightheadedness?"
                ),
            },
        }

        focused_queries = []

        for topic in topics.values():
            if any(alias in q for alias in topic["aliases"]):
                focused_queries.append(topic["query"])

        return focused_queries

    def search(self, query, k=3):
        """Search the original query and focused medical queries."""
        queries = [query]
        queries.extend(self._topic_queries(query))

        # Remove duplicate query strings.
        queries = list(dict.fromkeys(queries))

        best_results = {}

        for search_query in queries:
            q_emb = encode([search_query]).astype(np.float32)

            scores, indices = self.index.search(
                q_emb,
                min(k, len(self.data)),
            )

            for score, idx in zip(scores[0], indices[0]):
                if idx < 0 or idx >= len(self.data):
                    continue

                doc = self.data[int(idx)]
                doc_key = str(doc.get("id", idx))
                score = float(score)

                if (
                    doc_key not in best_results
                    or score > best_results[doc_key][0]
                ):
                    best_results[doc_key] = (score, doc)

        results = sorted(
            best_results.values(),
            key=lambda item: item[0],
            reverse=True,
        )

        return (
            np.asarray(
                [score for score, _ in results],
                dtype=np.float32,
            ),
            [doc for _, doc in results],
        )
