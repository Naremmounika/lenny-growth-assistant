from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from app.services.agent import run_growth_agent


router = APIRouter(
    prefix="/api/agent",
    tags=["Agent"],
)


class AgentRequest(BaseModel):
    question: str = Field(..., min_length=1)
    grounded_context: str = ""


class AgentResponse(BaseModel):
    provider: str
    model: str
    content: str


@router.post("/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest):
    try:
        content = await run_growth_agent(
            question=request.question,
            grounded_context=request.grounded_context,
        )

        import os

        return AgentResponse(
            provider="claude-agent-sdk",
            model=os.getenv(
                "AGENT_MODEL",
                "claude-sonnet-4-6",
            ),
            content=content,
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {str(exc)}",
        ) from exc