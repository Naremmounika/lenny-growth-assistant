from fastapi import APIRouter

from app.config import settings

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
    }
