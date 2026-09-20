import asyncio
import json
import re
import sys
from pathlib import Path

from sentence_transformers import SentenceTransformer
from sqlalchemy import text

# Make backend/ available so "app" imports work
sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent),
)

from app.db.session import AsyncSessionLocal


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

TRANSCRIPTS_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "transcripts"
)

CHUNK_SIZE = 600
CHUNK_OVERLAP = 100

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# ---------------------------------------------------------
# Transcript parsing
# ---------------------------------------------------------

def parse_transcript(file_path: Path):
    """
    Expected transcript format:

    Episode: Episode title
    Guest: Guest name

    [00:01:20]
    Transcript text...

    [00:03:45]
    More transcript text...
    """

    content = file_path.read_text(encoding="utf-8")

    # Episode title
    episode_match = re.search(
        r"^Episode:\s*(.+)$",
        content,
        flags=re.MULTILINE | re.IGNORECASE,
    )

    # Guest name
    guest_match = re.search(
        r"^Guest:\s*(.+)$",
        content,
        flags=re.MULTILINE | re.IGNORECASE,
    )

    episode_title = (
        episode_match.group(1).strip()
        if episode_match
        else file_path.stem
    )

    guest_name = (
        guest_match.group(1).strip()
        if guest_match
        else "Unknown Guest"
    )

    # Remove metadata headers
    body = re.sub(
        r"^Episode:\s*.+$",
        "",
        content,
        flags=re.MULTILINE | re.IGNORECASE,
    )

    body = re.sub(
        r"^Guest:\s*.+$",
        "",
        body,
        flags=re.MULTILINE | re.IGNORECASE,
    )

    # Find timestamped sections
    pattern = re.compile(
        r"\[(\d{2}:\d{2}:\d{2})\]\s*(.*?)(?=\n\[\d{2}:\d{2}:\d{2}\]|\Z)",
        flags=re.DOTALL,
    )

    matches = pattern.findall(body)

    sections = []

    for timestamp, text_content in matches:
        cleaned_text = " ".join(text_content.split())

        if cleaned_text:
            sections.append(
                {
                    "timestamp": timestamp,
                    "content": cleaned_text,
                }
            )

    # If no timestamps were found, treat the whole body as one section
    if not sections:
        cleaned_body = " ".join(body.split())

        if cleaned_body:
            sections.append(
                {
                    "timestamp": None,
                    "content": cleaned_body,
                }
            )

    return episode_title, guest_name, sections


# ---------------------------------------------------------
# Chunking
# ---------------------------------------------------------

def chunk_text(
    text_content: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
):
    """
    Split text into overlapping word-based chunks.

    600 words with 100 words of overlap is used as a
    lightweight approximation of the assignment's
    500-800 token chunking requirement.
    """

    words = text_content.split()

    if not words:
        return []

    if len(words) <= chunk_size:
        return [text_content]

    chunks = []

    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))

        chunk = " ".join(words[start:end]).strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks


# ---------------------------------------------------------
# Embedding helper
# ---------------------------------------------------------

def create_embedding(model, text_content: str):
    """
    Create a 384-dimensional embedding using
    all-MiniLM-L6-v2.
    """

    embedding = model.encode(
        text_content,
        normalize_embeddings=True,
    )

    return embedding.tolist()


def embedding_to_pgvector(embedding):
    """
    Convert Python list to PostgreSQL pgvector format.
    """

    return "[" + ",".join(
        str(float(value))
        for value in embedding
    ) + "]"


# ---------------------------------------------------------
# Main ingestion
# ---------------------------------------------------------

async def ingest():

    print("Loading embedding model...")

    model = SentenceTransformer(
        EMBEDDING_MODEL
    )

    print("Embedding model loaded.")

    transcript_files = sorted(
        TRANSCRIPTS_DIR.glob("*.txt")
    )

    if not transcript_files:
        print(
            f"No transcript files found in: "
            f"{TRANSCRIPTS_DIR}"
        )
        return

    print(
        f"Found {len(transcript_files)} "
        f"transcript file(s)."
    )

    async with AsyncSessionLocal() as session:

        for file_path in transcript_files:

            print()
            print("=" * 60)
            print(f"Processing: {file_path.name}")
            print("=" * 60)

            episode_title, guest_name, sections = (
                parse_transcript(file_path)
            )

            print(
                f"Episode: {episode_title}"
            )

            print(
                f"Guest: {guest_name}"
            )

            print(
                f"Sections: {len(sections)}"
            )

            total_chunks = 0

            for section in sections:

                chunks = chunk_text(
                    section["content"]
                )

                for chunk_index, chunk in enumerate(chunks):

                    embedding = create_embedding(
                        model,
                        chunk,
                    )

                    # Confirm expected embedding size
                    if len(embedding) != 384:
                        raise ValueError(
                            f"Expected 384 dimensions, "
                            f"got {len(embedding)}"
                        )

                    embedding_string = (
                        embedding_to_pgvector(
                            embedding
                        )
                    )

                    metadata = {
                        "source_file": file_path.name,
                        "chunk_index": chunk_index,
                    }

                    insert_query = text(
                        """
                        INSERT INTO transcript_chunks (
                            episode_title,
                            guest_name,
                            content,
                            timestamp,
                            topic,
                            metadata_json,
                            embedding
                        )
                        VALUES (
                            :episode_title,
                            :guest_name,
                            :content,
                            :timestamp,
                            :topic,
                            CAST(:metadata_json AS jsonb),
                            CAST(:embedding AS vector)
                        )
                        """
                    )

                    await session.execute(
                        insert_query,
                        {
                            "episode_title": episode_title,
                            "guest_name": guest_name,
                            "content": chunk,
                            "timestamp": section["timestamp"],
                            "topic": None,
                            "metadata_json": json.dumps(metadata),
                            "embedding": embedding_string,
                        },
                    )

                    total_chunks += 1

                    print(
                        f"  Inserted chunk "
                        f"{total_chunks}"
                    )

            await session.commit()

            print()
            print(
                f"Inserted {total_chunks} "
                f"chunk(s)."
            )

            print(
                f"Finished: {file_path.name}"
            )

    print()
    print("=" * 60)
    print("Transcript ingestion completed successfully.")
    print("=" * 60)


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(ingest())