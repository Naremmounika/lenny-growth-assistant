import os
from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions, query


PROJECT_ROOT = Path(__file__).resolve().parents[2]


async def run_growth_agent(
    question: str,
    grounded_context: str = "",
) -> str:
    """
    Run the Claude Agent SDK as the agentic orchestration layer.

    The agent is intentionally restricted to text-only interaction.
    Retrieved transcript evidence is supplied as context so the agent
    does not independently browse external sources.
    """

    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not configured. "
            "Agent mode requires an Anthropic API key."
        )

    model = os.getenv(
        "AGENT_MODEL",
        "claude-sonnet-4-6",
    )

    prompt = f"""
You are the Lenny Growth Assistant agent.

Your job is to answer the user's product and growth question
using ONLY the supplied transcript evidence.

USER QUESTION:
{question}

TRANSCRIPT EVIDENCE:
{grounded_context}

Rules:
- Use only the supplied transcript evidence for factual claims.
- Do not invent episodes, guests, quotes, timestamps, or facts.
- If the evidence does not contain enough information, clearly say so.
- Keep relevant source citations.
- Give a useful, concise answer.
""".strip()

    options = ClaudeAgentOptions(
        model=model,
        cwd=str(PROJECT_ROOT),
        allowed_tools=[],
        max_turns=1,
    )

    output_parts = []

    async for message in query(
        prompt=prompt,
        options=options,
    ):
        # Avoid depending on SDK message subclasses so this remains
        # compatible with SDK updates.
        if hasattr(message, "content"):
            content = message.content

            if isinstance(content, list):
                for block in content:
                    if hasattr(block, "text"):
                        output_parts.append(block.text)

            elif isinstance(content, str):
                output_parts.append(content)

        if hasattr(message, "result") and message.result:
            output_parts.append(message.result)

    result = "\n".join(
        part.strip()
        for part in output_parts
        if part and part.strip()
    )

    if not result:
        raise RuntimeError(
            "Claude Agent SDK returned an empty response."
        )

    return result