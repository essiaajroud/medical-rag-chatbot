import os

from dotenv import load_dotenv


load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = os.getenv(
    "GEMINI_MODEL_NAME",
    "gemini-flash-lite-latest"
)

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"
)

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "phi3"
)

LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "gemini"
).strip().lower()

if LLM_PROVIDER not in {"gemini", "ollama"}:
    raise ValueError(
        "LLM_PROVIDER must be either 'gemini' or 'ollama'"
    )

TOP_K = int(os.getenv("TOP_K", "2"))

SIM_THRESHOLD = float(
    os.getenv("SIM_THRESHOLD", "0.35")
)

RAG_CONTEXT_THRESHOLD = float(
    os.getenv("RAG_CONTEXT_THRESHOLD", "0.35")
)