from dataclasses import dataclass


@dataclass
class DocumentChunk:
    text: str
    source: str
    page: int
    chunk_id: str


def chunk_text(
    text: str,
    chunk_size: int = 800,
    chunk_overlap: int = 150,
) -> list[str]:
    """
    Split text into overlapping word-based chunks.

    Args:
        text: Input document text.
        chunk_size: Approximate number of words per chunk.
        chunk_overlap: Number of words shared between chunks.

    Returns:
        List of text chunks.
    """

    words = text.split()

    if not words:
        return []

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks = []

    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])

        chunks.append(chunk)

        if end >= len(words):
            break

        start = end - chunk_overlap

    return chunks