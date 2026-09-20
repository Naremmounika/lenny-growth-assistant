from app.services.provider import generate_answer


async def generate_artifact_content(
    request: str,
    answer: str,
    artifact_type: str,
) -> str:

    if artifact_type == "markdown":
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

    elif artifact_type == "html":
        prompt = f"""
Create a complete, self-contained HTML artifact based ONLY on
the following grounded answer.

User request:
{request}

Grounded answer:
{answer}

Return ONLY valid HTML.

Requirements:
- Return a complete HTML document.
- Include <!DOCTYPE html>.
- Include <html>, <head>, and <body>.
- Use semantic HTML elements.
- Create a clean professional growth playbook.
- Include a clear title.
- Include a summary section.
- Include key insights.
- Include actionable recommendations.
- Include relevant citations from the grounded answer.
- Do not use external JavaScript.
- Do not use external resources.
- Do not invent facts.
- Do not include Markdown code fences.
""".strip()

    elif artifact_type == "css":
        prompt = f"""
Create CSS for a professional growth playbook based ONLY on
the following grounded answer.

User request:
{request}

Grounded answer:
{answer}

Return ONLY valid CSS.

Requirements:
- Style headings, sections, cards, lists, citations, and buttons.
- Use readable spacing and typography.
- Create a clean professional layout.
- Do not include HTML.
- Do not include JavaScript.
- Do not include Markdown code fences.
- Do not invent factual content.
""".strip()

    elif artifact_type == "html_css":
        prompt = f"""
Create a complete self-contained HTML + CSS artifact based ONLY
on the following grounded answer.

User request:
{request}

Grounded answer:
{answer}

Return ONLY a complete HTML document.

Requirements:
- Include <!DOCTYPE html>.
- Include <html>, <head>, and <body>.
- Put all CSS inside a single <style> element.
- Use semantic HTML.
- Create a clean professional growth playbook.
- Include:
  - Clear title
  - Short summary
  - Key insights
  - Actionable recommendations
  - Relevant citations
- Make the layout visually polished.
- Use cards, sections, lists, spacing, and readable typography.
- Do not use external CSS.
- Do not use external JavaScript.
- Do not include Markdown code fences.
- Do not invent facts.
- Use only information supported by the grounded answer.
""".strip()

    else:
        raise ValueError(f"Unsupported artifact type: {artifact_type}")

    return await generate_answer(prompt)