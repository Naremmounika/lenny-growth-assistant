import os
from typing import Any

from sqlalchemy import text

from app.db.session import AsyncSessionLocal


DEFAULT_TOP_K = 5
DEFAULT_THRESHOLD = 0.35
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Use embeddings by default locally.
# Set USE_EMBEDDINGS=false on low-memory deployments such as Render Free.
USE_EMBEDDINGS = os.getenv("USE_EMBEDDINGS", "true").lower() == "true"

embedding_model = None

if USE_EMBEDDINGS:
    from sentence_transformers import SentenceTransformer

    embedding_model = SentenceTransformer(EMBEDDING_MODEL)


async def search_transcript_chunks(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    threshold: float = DEFAULT_THRESHOLD,
) -> list[dict[str, Any]]:

    if not query or not query.strip():
        return []

    top_k = max(1, min(top_k, 10))

    # ---------------------------------------------------------
    # Vector RAG mode
    # ---------------------------------------------------------
    if USE_EMBEDDINGS and embedding_model is not None:

        query_embedding = embedding_model.encode(
            query.strip(),
            normalize_embeddings=True,
        ).tolist()

        embedding_string = (
            "["
            + ",".join(
                str(value)
                for value in query_embedding
            )
            + "]"
        )

        sql = text(
            """
            SELECT
                id,
                episode_title,
                guest_name,
                content,
                timestamp,
                topic,
                metadata_json,
                1 - (
                    embedding <=> CAST(:query_embedding AS vector)
                ) AS similarity
            FROM transcript_chunks
            WHERE embedding IS NOT NULL
              AND (
                  1 - (
                      embedding <=> CAST(:query_embedding AS vector)
                  )
              ) >= :threshold
            ORDER BY embedding <=> CAST(:query_embedding AS vector)
            LIMIT :top_k
            """
        )

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                sql,
                {
                    "query_embedding": embedding_string,
                    "threshold": threshold,
                    "top_k": top_k,
                },
            )

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

    # ---------------------------------------------------------
    # Lightweight fallback mode
    # ---------------------------------------------------------
    # Used when USE_EMBEDDINGS=false, for example on Render Free.
    # This avoids loading PyTorch/SentenceTransformers into memory.
    search_term = f"%{query.strip()}%"

    sql = text(
        """
        SELECT
            id,
            episode_title,
            guest_name,
            content,
            timestamp,
            topic,
            metadata_json
        FROM transcript_chunks
        WHERE
            content ILIKE :search_term
            OR episode_title ILIKE :search_term
            OR guest_name ILIKE :search_term
            OR topic ILIKE :search_term
        ORDER BY created_at DESC
        LIMIT :top_k
        """
    )

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            sql,
            {
                "search_term": search_term,
                "top_k": top_k,
            },
        )

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
            "similarity": 1.0,
        }
        for row in rows
    ]