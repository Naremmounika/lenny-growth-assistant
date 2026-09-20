from app.services.provider import generate_answer


SHIP30_PRINCIPLES = """
Write a Ship 30 for 30 style essay.

Writing principles:
- Start with a strong hook that creates curiosity.
- Focus on one clear idea rather than many unrelated ideas.
- Use a clear narrative progression from problem to insight to takeaway.
- Make the writing practical and useful to the reader.
- Use short paragraphs for readability.
- Use headings when they improve structure.
- Use bullets when they make information easier to scan.
- Use selective bold emphasis for important ideas.
- Prefer concrete examples over vague statements.
- End with a specific and actionable takeaway.
- Avoid unnecessary introductions and filler.
- Do not invent facts, examples, quotes, guests, episodes, or claims.
- Keep all factual claims grounded in the supplied transcript evidence.
- Preserve relevant transcript citations.
- Target approximately 1,250 words.
"""


async def generate_ship30_essay(
    question: str,
    grounded_answer: str,
) -> str:
    prompt = f"""
You are the Ship 30 for 30 writing skill inside Lenny Growth Assistant.

Your task is to transform a grounded answer into a useful,
approximately 1,250-word essay.

{SHIP30_PRINCIPLES}

USER REQUEST:
{question}

GROUNDED ANSWER:
{grounded_answer}

IMPORTANT:
- The grounded answer is the only source of factual information.
- Do not add outside knowledge.
- Do not invent information.
- Keep relevant transcript citations.
- Return ONLY the finished Markdown essay.
- Do not explain your process.
- Do not use a Markdown code fence.

The essay should contain:
1. A strong opening hook.
2. A clear central idea.
3. A logical narrative progression.
4. Useful insights supported by the grounded answer.
5. Practical recommendations.
6. A specific final takeaway.

Write the essay now.
""".strip()

    return await generate_answer(prompt)