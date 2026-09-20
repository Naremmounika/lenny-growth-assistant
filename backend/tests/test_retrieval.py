import pytest

from app.services.retrieval import search_transcript_chunks


@pytest.mark.asyncio
async def test_retrieval_returns_relevant_chunks():
    results = await search_transcript_chunks(
        query="How do you build a product people love?",
        top_k=5,
    )

    assert results is not None
    assert len(results) > 0

    first_result = results[0]

    assert "content" in first_result
    assert first_result["content"]

    assert "episode_title" in first_result
    assert first_result["episode_title"]

    assert "similarity" in first_result

    assert first_result["similarity"] >= 0.35