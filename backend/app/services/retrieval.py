from typing import Any

from sqlalchemy import text

from app.db.session import AsyncSessionLocal


DEFAULT_TOP_K = 5


async def search_transcript_chunks(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    threshold: float = 0.0,
) -> list[dict[str, Any]]:

    if not query or not query.strip():
        return []

    top_k = max(1, min(top_k, 10))

    words = [
        word.lower()
        for word in query.split()
        if len(word) >= 3
    ]

    if not words:
        return []

    conditions = []
    params = {"top_k": top_k}

    for index, word in enumerate(words[:10]):
        key = f"word_{index}"
        conditions.append(
            f"LOWER(content) LIKE :{key}"
        )
        params[key] = f"%{word}%"

    where_clause = " OR ".join(conditions)

    sql = text(
        f"""
        SELECT
            id,
            episode_title,
            guest_name,
            content,
            timestamp,
            topic,
            metadata_json,
            1.0 AS similarity
        FROM transcript_chunks
        WHERE {where_clause}
        ORDER BY created_at DESC
        LIMIT :top_k
        """
    )

    async with AsyncSessionLocal() as session:
        result = await session.execute(sql, params)
        rows = result.mappings().all()

    return [
        {
            "id": str(row["id"]),
            "episode_title": row["episode_title"],
            "guest_name": row["guest_name"],
            "content": row["content"],
            "timestamp": row["timestamp"],
            "topic": row["topic"],
            "metadata": row["metadata_json"],
            "similarity": float(row["similarity"]),
        }
        for row in rows
    ]