import asyncio

from sqlalchemy import text
from app.database import engine


async def check():
    async with engine.connect() as conn:
        result = await conn.execute(
            text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
        )

        print("\nDatabase tables:")
        for row in result:
            print(f"  - {row[0]}")

    await engine.dispose()


asyncio.run(check())
