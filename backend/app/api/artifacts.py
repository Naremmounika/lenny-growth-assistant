from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.db_models import Artifact, Message
from app.services.artifact import generate_artifact_content


router = APIRouter(
    prefix="/api/artifacts",
    tags=["Artifacts"],
)


class ArtifactRequest(BaseModel):
    request: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)
    artifact_type: str = Field(default="markdown")
    message_id: UUID


class ArtifactResponse(BaseModel):
    artifact_id: str
    message_id: str
    artifact_type: str
    content: str


@router.post("/generate", response_model=ArtifactResponse)
async def generate_artifact(request: ArtifactRequest):
    try:
        artifact_type = request.artifact_type.lower().strip()

        allowed_types = {
            "markdown",
            "html",
            "css",
            "html_css",
        }

        if artifact_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Unsupported artifact type. "
                    "Use markdown, html, css, or html_css."
                ),
            )

        async with AsyncSessionLocal() as db:
            message_result = await db.execute(
                select(Message)
                .where(Message.id == request.message_id)
            )

            message = message_result.scalar_one_or_none()

            if message is None:
                raise HTTPException(
                    status_code=404,
                    detail="Message not found.",
                )

        content = await generate_artifact_content(
            request=request.request,
            answer=request.answer,
            artifact_type=artifact_type,
        )

        async with AsyncSessionLocal() as db:
            artifact = Artifact(
                message_id=request.message_id,
                artifact_type=artifact_type,
                content=content,
            )

            db.add(artifact)

            await db.commit()
            await db.refresh(artifact)

            return ArtifactResponse(
                artifact_id=str(artifact.id),
                message_id=str(artifact.message_id),
                artifact_type=artifact.artifact_type,
                content=artifact.content,
            )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Artifact generation failed: {str(exc)}",
        ) from exc