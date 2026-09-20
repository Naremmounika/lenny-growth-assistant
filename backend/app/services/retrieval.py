from typing import Any

from sentence_transformers import SentenceTransformer
from sqlalchemy import text

from app.db.session import AsyncSessionLocal


DEFAULT_TOP_K = 5
DEFAULT_THRESHOLD = 0.35
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# Load the embedding model once when the module starts.
embedding_model = SentenceTransformer(EMBEDDING_MODEL)


async def search_transcript_chunks(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    threshold: float = DEFAULT_THRESHOLD,
) -> list[dict[str, Any]]:

    if not query or not query.strip():
        return []

    top_k = max(1, min(top_k, 10))

    # Create the same type of embedding that was used
    # during transcript ingestion.
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