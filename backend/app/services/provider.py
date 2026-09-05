import os

from openai import AsyncOpenAI

from app.services.llm import generate_with_ollama


async def generate_answer(prompt: str) -> str:
    provider = os.getenv(
        "DEFAULT_PROVIDER",
        "ollama",
    ).lower()

    if provider == "ollama":
        return await generate_with_ollama(prompt)

    if provider == "cloud":
        api_key = os.getenv("CLOUD_API_KEY")
        model = os.getenv(
            "CLOUD_MODEL",
            "gpt-4o-mini",
        )

        if not api_key:
            raise RuntimeError(
                "CLOUD_API_KEY is not configured"
            )

        client = AsyncOpenAI(api_key=api_key)

        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.2,
        )

        return response.choices[0].message.content or ""

    raise RuntimeError(
        f"Unsupported LLM provider: {provider}"
    )