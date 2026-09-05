from app.services.provider import generate_answer 



def build_context(results: list[dict]) -> str:
    if not results:
        return ""

    context_parts = []

    for index, result in enumerate(results, start=1):
        episode = result.get("episode_title") or "Unknown Episode"
        guest = result.get("guest_name") or "Unknown Guest"
        timestamp = result.get("timestamp") or "Unknown timestamp"
        topic = result.get("topic") or "General"
        content = result.get("content", "")

        context_parts.append(
            f"""
SOURCE {index}
Episode: {episode}
Guest: {guest}
Timestamp: {timestamp}
Topic: {topic}

Transcript:
{content}
""".strip()
        )

    return "\n\n".join(context_parts)


def build_conversation_context(
    messages: list[dict] | None,
) -> str:
    if not messages:
        return ""

    recent_messages = messages[-10:]

    parts = []

    for message in recent_messages:
        role = message.get("role", "").upper()
        content = message.get("content", "")

        if role in {"USER", "ASSISTANT"} and content:
            parts.append(f"{role}: {content}")

    return "\n".join(parts)


def build_grounded_prompt(
    question: str,
    results: list[dict],
    messages: list[dict] | None = None,
) -> str:
    transcript_context = build_context(results)
    conversation_context = build_conversation_context(messages)

    if conversation_context:
        conversation_section = f"""
PREVIOUS CONVERSATION:

{conversation_context}
""".strip()
    else:
        conversation_section = "No previous conversation."

    return f"""
You are Lenny Growth Assistant.

You answer questions about Lenny's podcast transcripts.

Your answer must be grounded ONLY in the transcript evidence
provided below.

RULES:

1. Use the previous conversation to understand follow-up questions.
2. Do not invent information.
3. Do not use outside knowledge.
4. If the transcript evidence does not support an answer,
   say that the available transcripts do not provide enough
   evidence.
5. Keep the answer concise and useful.
6. Every factual claim based on transcript evidence must have
   a citation.
7. Citations MUST use the exact episode, guest, and timestamp
   from the SOURCE that supports the claim.
8. NEVER cite a source merely because it was retrieved.
9. If a source does not support a claim, do not cite it.
10. Do not invent timestamps.
11. Do not invent episode titles or guest names.
12. For follow-up questions, use the previous conversation to
    resolve references such as "it", "that", "this", or "they".

CITATION FORMAT:

[Episode: <episode title>, Guest: <guest>, Timestamp: <timestamp>]

{conversation_section}

TRANSCRIPT EVIDENCE:

{transcript_context}

CURRENT USER QUESTION:

{question}

ANSWER:
""".strip()


async def generate_grounded_answer(
    question: str,
    results: list[dict],
    messages: list[dict] | None = None,
) -> str:
    if not results:
        return (
            "I couldn't find enough relevant transcript evidence "
            "to answer that question."
        )

    prompt = build_grounded_prompt(
        question=question,
        results=results,
        messages=messages,
    )

    return await generate_answer(prompt)