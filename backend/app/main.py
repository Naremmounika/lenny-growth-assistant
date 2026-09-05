from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.api.health import router as health_router
from app.api.sessions import router as sessions_router
from app.api.retrieval import router as retrieval_router
from app.api.answer import router as answer_router
from app.api.artifacts import router as artifacts_router

from app.models import (
    Artifact,
    Message,
    Session,
    TranscriptChunk,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health_router)
app.include_router(sessions_router)
app.include_router(retrieval_router)
app.include_router(answer_router)
app.include_router(artifacts_router)

@app.get("/")
async def root():
    return {
        "message": "Lenny Growth Assistant API",
        "status": "running",
    }
