from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SessionCreate(BaseModel):
    title: str = "New Conversation"


class SessionResponse(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageCreate(BaseModel):
    role: str
    content: str
    sources: list | None = None


class MessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    role: str
    content: str
    sources: list | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
