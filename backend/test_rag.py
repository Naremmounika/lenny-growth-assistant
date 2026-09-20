import asyncio

from app.services.retrieval import search_transcript_chunks
from app.services.answer import generate_grounded_answer


async def main():
    question = "How do you build a product people love?"

    results = await search_transcript_chunks(question)

    print(f"\nRetrieved {len(results)} chunks.")

    answer = await generate_grounded_answer(
        question,
        results,
    )

    print("\nANSWER:\n")
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())