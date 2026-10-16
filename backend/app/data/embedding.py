
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer(
    "paraphrase-multilingual-MiniLM-L12-v2"
)


def encode(texts):
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    print(
        "EMBEDDING NORMS:",
        np.linalg.norm(embeddings, axis=1)
    )

    return embeddings
