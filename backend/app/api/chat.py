import json
from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.db_models import Message, Session
from app.services.answer import build_grounded_prompt
from app.services.retrieval import search_transcript_chunks
from app.services.llm import OLLAMA_BASE_URL, OLLAMA_MODEL


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


class ChatRequest(BaseModel):
    session_id: UUID
    message: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=10)


async def get_conversation_messages(
    session_id: UUID,
) -> list[dict]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at.asc())
        )

        messages = result.scalars().all()

    return [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in messages
    ]


async def save_message(
    session_id: UUID,
    role: str,
    content: str,
    sources: list | None = None,
):
    async with AsyncSessionLocal() as db:
        message = Message(
            session_id=session_id,
            role=role,
            content=content,
            sources=sources or [],
        )

        db.add(message)

        await db.commit()
        await db.refresh(message)

        return message.id


@router.post("")
async def chat(request: ChatRequest):
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Session)
            .where(Session.id == request.session_id)
        )

        session = result.scalar_one_or_none()

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    conversation_messages = await get_conversation_messages(
        request.session_id
    )

    results = await search_transcript_chunks(
        query=request.message,
        top_k=request.top_k,
    )

    prompt = build_grounded_prompt(
        question=request.message,
        results=results,
        messages=conversation_messages,
    )

    sources = [
        {
            "episode_title": result["episode_title"],
            "guest_name": result["guest_name"],
            "timestamp": result["timestamp"],
            "topic": result["topic"],
            "content": result["content"],
            "similarity": result["similarity"],
        }
        for result in results
    ]

    await save_message(
        session_id=request.session_id,
        role="user",
        content=request.message,
    )

    async def generate():
        full_answer = ""

        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": 0.2,
            },
        }

        try:
            timeout = httpx.Timeout(
                connect=10.0,
                read=120.0,
                write=30.0,
                pool=30.0,
            )

            async with httpx.AsyncClient(
                timeout=timeout
            ) as client:
                async with client.stream(
                    "POST",
                    f"{OLLAMA_BASE_URL.rstrip('/')}/api/generate",
                    json=payload,
                ) as response:

                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if not line:
                            continue

                        data = json.loads(line)

                        token = data.get("response", "")

                        if token:
                            full_answer += token

                            yield (
                                json.dumps(
                                    {
                                        "type": "token",
                                        "content": token,
                                    }
                                )
                                + "\n"
                            )

                        if data.get("done"):
                            break

            assistant_message_id = await save_message(
                session_id=request.session_id,
                role="assistant",
                content=full_answer,
                sources=sources,
            )

            yield (
                json.dumps(
                    {
                        "type": "done",
                        "message_id": str(assistant_message_id),
                        "sources": sources,
                    }
                )
                + "\n"
            )

        except Exception as exc:
            yield (
                json.dumps(
                    {
                        "type": "error",
                        "message": str(exc),
                    }
                )
                + "\n"
            )

    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson",
    )