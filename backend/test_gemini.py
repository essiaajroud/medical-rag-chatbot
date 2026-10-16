import asyncio

from app.llm.gemini_client import generate


async def main():
    response = await generate(
        "Réponds simplement en français : "
        "qu'est-ce que la fièvre ?"
    )

    print("\n--- GEMINI RESPONSE ---\n")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())