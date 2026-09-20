import pytest

from app.services import agent


@pytest.mark.asyncio
async def test_agent_requires_api_key(monkeypatch):
    monkeypatch.delenv(
        "ANTHROPIC_API_KEY",
        raising=False,
    )

    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        await agent.run_growth_agent(
            question="What is product-market fit?"
        )