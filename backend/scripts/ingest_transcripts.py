import sys
from pathlib import Path

# Make backend/ available so "app" imports work
sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent)
)

import asyncio
import json
import re

from sqlalchemy import text
from sentence_transformers import SentenceTransformer

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
    Parse transcript files using this format:

    Episode: Episode title
    Guest: Guest name

    [00:01:20]
    Transcript text...

    [00:03:45]
    More transcript text...
    """

    content = file_path.read_text(
        encoding="utf-8"
    )

    # Extract episode title
    episode_match = re.search(
        r"Episode:\s*(.+)",
        content,
        re.IGNORECASE,
    )

    # Extract guest name
    guest_match = re.search(
        r"Guest:\s*(.+)",
        content,
        re.IGNORECASE,
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
        r"^Episode:.*$",
        "",
        content,
        flags=re.MULTILINE | re.IGNORECASE,
    )

    body = re.sub(
        r"^Guest:.*$",
        "",
        body,
        flags=re.MULTILINE | re.IGNORECASE,
    )

    # Find timestamped transcript sections
    pattern = (
        r"\[(\d{2}:\d{2}:\d{2})\]\s*"
        r"(.*?)(?=\n\[\d{2}:\d{2}:\d{2}\]|\Z)"
    )

    matches = re.findall(
        pattern,
        body,
        flags=re.DOTALL,
    )

    sections = []

    for timestamp, text_content in matches:

        cleaned_text = " ".join(
            text_content.split()
        )

        if cleaned_text:
            sections.append(
                {
                    "timestamp": timestamp,
                    "content": cleaned_text,
                }
            )

    return (
        episode_title,
        guest_name,
        sections,
    )


# ---------------------------------------------------------
# Chunking
# ---------------------------------------------------------

def chunk_text(
    text_content,
    chunk_size=CHUNK_SIZE,
    overlap=CHUNK_OVERLAP,
):
    """
    Split text into overlapping chunks.

    This uses whitespace tokens as a lightweight
    approximation for token-based chunking.
    """

    words = text_content.split()

    if not words:
        return []

    if len(words) <= chunk_size:
        return [text_content]

    chunks = []

    start = 0

    while start < len(words):

        end = min(
            start + chunk_size,
            len(words),
        )

        chunk = " ".join(
            words[start:end]
        )

        if chunk.strip():
            chunks.append(
                chunk.strip()
            )

        # Stop when we've reached the end
        if end >= len(words):
            break

        # Move forward while keeping overlap
        start = end - overlap

    return chunks


# ---------------------------------------------------------
# Main ingestion
# ---------------------------------------------------------

async def ingest():

    print("Loading embedding model...")

    model = SentenceTransformer(
        EMBEDDING_MODEL
    )

    print("Embedding model loaded.")

    # Find transcript files
    transcript_files = list(
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

    # Open database session
    async with AsyncSessionLocal() as session:

        for file_path in transcript_files:

            print(
                f"\nProcessing: "
                f"{file_path.name}"
            )

            # Parse transcript
            (
                episode_title,
                guest_name,
                sections,
            ) = parse_transcript(
                file_path
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

            # Process each timestamp section
            for section in sections:

                chunks = chunk_text(
                    section["content"]
                )

                for chunk_index, chunk in enumerate(
                    chunks
                ):

                    # Generate embedding
                    embedding = model.encode(
                        chunk
                    ).tolist()

                    # Convert Python list to pgvector format
                    embedding_string = (
                        "["
                        + ",".join(
                            str(value)
                            for value in embedding
                        )
                        + "]"
                    )

                    # Metadata
                    metadata = {
                        "source_file": file_path.name,
                        "chunk_index": chunk_index,
                    }

                    # Insert into PostgreSQL
                    query = text(
                        """
                        INSERT INTO transcript_chunks
                        (
                            episode_title,
                            guest_name,
                            content,
                            timestamp,
                            topic,
                            metadata_json,
                            embedding
                        )
                        VALUES
                        (
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
                        query,
                        {
                            "episode_title": episode_title,
                            "guest_name": guest_name,
                            "content": chunk,
                            "timestamp": section[
                                "timestamp"
                            ],
                            "topic": None,
                            "metadata_json": json.dumps(
                                metadata
                            ),
                            "embedding": embedding_string,
                        },
                    )

                    total_chunks += 1

            # Commit this transcript
            await session.commit()

            print(
                f"Inserted {total_chunks} "
                f"chunk(s)."
            )

            print(
                f"Finished: {file_path.name}"
            )

    print(
        "\nTranscript ingestion "
        "completed successfully."
    )


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(ingest())