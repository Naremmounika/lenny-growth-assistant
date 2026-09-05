from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.db_models import Message, Session
from app.models.schemas import (
    MessageCreate,
    MessageResponse,
    SessionCreate,
    SessionResponse,
)

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


@router.post(
    "",
    response_model=SessionResponse,
    status_code=201,
)
async def create_session(
    data: SessionCreate,
    db: AsyncSession = Depends(get_db),
):
    session = Session(title=data.title)

    db.add(session)
    await db.commit()
    await db.refresh(session)

    return session


@router.get(
    "",
    response_model=list[SessionResponse],
)
async def list_sessions(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Session)
        .order_by(Session.updated_at.desc())
    )

    return result.scalars().all()


@router.get(
    "/{session_id}",
)
async def get_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Session).where(Session.id == session_id)
    )

    session = result.scalar_one_or_none()

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    messages_result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
    )

    messages = messages_result.scalars().all()

    return {
        "id": session.id,
        "title": session.title,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "messages": messages,
    }


@router.post(
    "/{session_id}/messages",
    response_model=MessageResponse,
    status_code=201,
)
async def create_message(
    session_id: UUID,
    data: MessageCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Session).where(Session.id == session_id)
    )

    session = result.scalar_one_or_none()

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    message = Message(
        session_id=session_id,
        role=data.role,
        content=data.content,
        sources=data.sources,
    )

    db.add(message)

    session.updated_at = session.updated_at

    await db.commit()
    await db.refresh(message)

    return message
