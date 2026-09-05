from app.services.provider import generate_answer


async def generate_markdown_artifact(
    request: str,
    answer: str,
) -> str:
    prompt = f"""
Create a useful Markdown artifact based ONLY on the
following grounded answer.

User request:
{request}

Grounded answer:
{answer}

Return only Markdown.

Include:
- Clear title
- Short summary
- Key insights
- Actionable recommendations
- Relevant citations from the answer

Do not invent facts.
""".strip()

    return await generate_answer(prompt)