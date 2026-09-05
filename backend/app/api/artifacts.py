from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.artifact import generate_markdown_artifact


router = APIRouter(
    prefix="/api/artifacts",
    tags=["Artifacts"],
)


class ArtifactRequest(BaseModel):
    request: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)


class ArtifactResponse(BaseModel):
    artifact_type: str
    content: str


@router.post("/generate", response_model=ArtifactResponse)
async def generate_artifact(request: ArtifactRequest):
    try:
        content = await generate_markdown_artifact(
            request=request.request,
            answer=request.answer,
        )

        return ArtifactResponse(
            artifact_type="markdown",
            content=content,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Artifact generation failed: {str(exc)}",
        ) from exc