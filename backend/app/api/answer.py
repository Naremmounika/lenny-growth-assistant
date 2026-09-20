from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models import Message

from app.services.answer import generate_grounded_answer
from app.services.retrieval import search_transcript_chunks


router = APIRouter(
    prefix="/api/answer",
    tags=["Answer"],
)


class AnswerRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=10)
    session_id: str | None = None


class AnswerResponse(BaseModel):
    query: str
    answer: str
    sources: list[dict]
    session_id: str | None


async def get_conversation_messages(session_id: str) -> list[dict]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
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
    session_id: str,
    role: str,
    content: str,
    sources: list | None = None,
):
    async with AsyncSessionLocal() as session:
        message = Message(
            session_id=session_id,
            role=role,
            content=content,
            sources=sources or [],
        )

        session.add(message)
        await session.commit()


@router.post("", response_model=AnswerResponse)
async def answer_question(request: AnswerRequest):
    try:
        conversation_messages = []

        if request.session_id:
            conversation_messages = await get_conversation_messages(
                request.session_id
            )

        results = await search_transcript_chunks(
            query=request.query,
            top_k=request.top_k
        )

        answer = await generate_grounded_answer(
            question=request.query,
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
            }
            for result in results
        ]

        if request.session_id:
            await save_message(
                session_id=request.session_id,
                role="user",
                content=request.query,
            )

            await save_message(
                session_id=request.session_id,
                role="assistant",
                content=answer,
                sources=sources,
            )

        return AnswerResponse(
            query=request.query,
            answer=answer,
            sources=sources,
            session_id=request.session_id,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Answer generation failed: {str(exc)}",
        ) from exc