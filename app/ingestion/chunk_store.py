import json
from pathlib import Path

from app.ingestion.chunker import chunk_text


def create_chunks(pages: list[dict]) -> list[dict]:
    """
    Convert extracted PDF pages into structured document chunks.
    """

    chunks = []

    for page in pages:
        page_chunks = chunk_text(page["text"])

        for chunk_index, text in enumerate(page_chunks):
            chunks.append(
                {
                    "chunk_id": f"{page['source']}-p{page['page']}-c{chunk_index}",
                    "text": text,
                    "source": page["source"],
                    "page": page["page"],
                    "chunk_index": chunk_index,
                }
            )

    return chunks


def save_chunks(chunks: list[dict], output_path: str) -> None:
    """
    Save chunks to a JSON file.
    """

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(chunks, file, ensure_ascii=False, indent=2)

    print(f"Saved {len(chunks)} chunks to {path}")