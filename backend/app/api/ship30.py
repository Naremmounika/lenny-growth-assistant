from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.db_models import Message
from app.services.ship30 import generate_ship30_essay


router = APIRouter(prefix="/api/skills", tags=["Skills"])


class Ship30Request(BaseModel):
    message_id: UUID
    question: str = Field(..., min_length=1)


class Ship30Response(BaseModel):
    message_id: str
    artifact_type: str
    content: str


@router.post("/ship30", response_model=Ship30Response)
async def generate_ship30(request: Ship30Request):
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Message).where(Message.id == request.message_id)
        )
        message = result.scalar_one_or_none()

    if message is None:
        raise HTTPException(
            status_code=404,
            detail="Message not found.",
        )

    try:
        essay = await generate_ship30_essay(
            question=request.question,
            grounded_answer=message.content,
        )

        return Ship30Response(
            message_id=str(message.id),
            artifact_type="ship30",
            content=essay,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Ship 30 essay generation failed: {str(exc)}",
        ) from exc