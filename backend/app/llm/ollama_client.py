from app.core.config import OLLAMA_URL, MODEL_NAME
import httpx

async def generate(prompt):
    # Timeout augmenté pour les lectures (le modèle peut prendre du temps à générer)
    # pool: 10s, connect: 10s, read: 300s, write: 10s
    timeout = httpx.Timeout(10.0, read=300.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response =  await client.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            }
        )
    return response.json().get("response", "No response")