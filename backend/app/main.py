from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine

from app.api.health import router as health_router
from app.api.sessions import router as sessions_router
from app.api.retrieval import router as retrieval_router
from app.api.answer import router as answer_router
from app.api.artifacts import router as artifacts_router
from app.api.chat import router as chat_router
from app.api.ship30 import router as ship30_router

@asynccontextmanager
async def lifespan(app: FastAPI):
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
app.include_router(chat_router)
app.include_router(ship30_router)


@app.get("/")
async def root():
    return {
        "message": "Lenny Growth Assistant API",
        "status": "running",
    }