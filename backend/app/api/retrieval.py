from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.retrieval import search_transcript_chunks


router = APIRouter(
    prefix="/api/retrieval",
    tags=["Retrieval"],
)


class RetrievalRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=10)
    threshold: float = Field(default=0.65, ge=0.0, le=1.0)


class RetrievalResult(BaseModel):
    id: str
    episode_title: str
    guest_name: str | None
    content: str
    timestamp: str | None
    topic: str | None
    metadata: dict | None
    similarity: float


class RetrievalResponse(BaseModel):
    query: str
    results: list[RetrievalResult]
    count: int


@router.post("/search", response_model=RetrievalResponse)
async def retrieve_chunks(request: RetrievalRequest):
    try:
        results = await search_transcript_chunks(
            query=request.query,
            top_k=request.top_k,
            threshold=request.threshold,
        )

        return RetrievalResponse(
            query=request.query,
            results=results,
            count=len(results),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Retrieval failed: {str(exc)}",
        ) from exc