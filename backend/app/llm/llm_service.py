from app.llm.gemini_client import generate as gemini_generate
from app.llm.ollama_client import generate as ollama_generate
from app.core.config import LLM_PROVIDER


async def generate(prompt: str) -> str:
    if LLM_PROVIDER == "gemini":
        return await gemini_generate(prompt)

    if LLM_PROVIDER == "ollama":
        return await ollama_generate(prompt)

    raise ValueError(f"Unknown LLM provider: {LLM_PROVIDER}")
