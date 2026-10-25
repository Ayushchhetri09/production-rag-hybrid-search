from pathlib import Path

from app.ingestion.pdf_loader import extract_pdf_pages
from app.ingestion.chunk_store import create_chunks, save_chunks


RAW_DIR = Path("data/raw")
OUTPUT_PATH = Path("data/processed/chunks.json")


def main() -> None:
    pdf_files = list(RAW_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files found in {RAW_DIR.resolve()}"
        )

    pdf_path = pdf_files[0]

    print(f"Reading: {pdf_path.resolve()}")

    pages = extract_pdf_pages(str(pdf_path))

    print(f"Pages extracted: {len(pages)}")

    chunks = create_chunks(pages)

    print(f"Total chunks: {len(chunks)}")

    save_chunks(chunks, str(OUTPUT_PATH))


if __name__ == "__main__":
    main()