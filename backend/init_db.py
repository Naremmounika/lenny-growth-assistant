import asyncio

from sqlalchemy import text

from app.database import Base, engine
from app.models.db_models import Session, Message, Artifact, TranscriptChunk


async def init_database():
    async with engine.begin() as conn:
        print("Enabling pgvector extension...")

        await conn.execute(
            text("CREATE EXTENSION IF NOT EXISTS vector")
        )

        print("Creating database tables...")

        await conn.run_sync(Base.metadata.create_all)

        print("Database setup completed successfully!")


if __name__ == "__main__":
    asyncio.run(init_database())

