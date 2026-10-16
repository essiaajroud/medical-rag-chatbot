from google import genai
from app.core.config import GEMINI_API_KEY, GEMINI_MODEL_NAME

async def generate(prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY must be set when LLM_PROVIDER='gemini'")

    client = genai.Client(api_key=GEMINI_API_KEY)
    response = await client.aio.models.generate_content(
        model=GEMINI_MODEL_NAME,
        contents=prompt,
    )

    return response.text or "No response"
