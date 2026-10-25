import json
from pathlib import Path

from app.ingestion.pdf_loader import extract_pdf_pages
from app.ingestion.chunk_store import create_chunks, save_chunks
from app.retrieval.embeddings import EmbeddingModel
from app.database.qdrant_store import QdrantStore


CHUNKS_PATH = "data/processed/chunks.json"


class DocumentIngestionService:
    def __init__(
        self,
        chunks_path: str = CHUNKS_PATH,
        embedding_model=None,
        qdrant_store=None,
    ):
        self.chunks_path = Path(chunks_path)

        self.embedding_model = (
            embedding_model
            if embedding_model is not None
            else EmbeddingModel()
        )

        self.qdrant_store = (
            qdrant_store
            if qdrant_store is not None
            else QdrantStore()
        )

    def ingest_pdf(
        self,
        pdf_path: str,
        source_name: str | None = None,
    ):
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(
                f"PDF not found: {pdf_path}"
            )

        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError(
                "Only PDF files are supported."
            )

        print(
            f"Processing document: {pdf_path.name}"
        )

        pages = extract_pdf_pages(
            str(pdf_path)
        )

        source_name = (
            source_name or pdf_path.name
        )

        for page in pages:
            page["source"] = source_name

        if not pages:
            raise ValueError(
                "No readable text was found in the PDF."
            )

        print(
            f"Extracted {len(pages)} pages."
        )

        new_chunks = create_chunks(pages)

        if not new_chunks:
            raise ValueError(
                "No text chunks were created from the PDF."
            )

        print(
            f"Created {len(new_chunks)} chunks."
        )

        existing_chunks = []

        if self.chunks_path.exists():
            with self.chunks_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                existing_chunks = json.load(file)

        existing_sources = {
            chunk["source"]
            for chunk in existing_chunks
        }

        if source_name in existing_sources:
            raise ValueError(
                f"The document '{source_name}' "
                "has already been uploaded."
            )

        # Generate embeddings first.
        print("Generating embeddings...")

        texts = [
            chunk["text"]
            for chunk in new_chunks
        ]

        embeddings = self.embedding_model.encode(
            texts
        )

        print(
            f"Generated {len(embeddings)} embeddings."
        )

        # Index in Qdrant before updating chunks.json.
        print("Indexing chunks in Qdrant...")

        self.qdrant_store.upsert(
            embeddings=embeddings,
            chunks=new_chunks,
        )

        print(
            f"Added {len(new_chunks)} chunks to Qdrant."
        )

        # Update chunks.json only after Qdrant succeeds.
        all_chunks = (
            existing_chunks + new_chunks
        )

        save_chunks(
            all_chunks,
            str(self.chunks_path),
        )

        print(
            f"Updated chunk store with "
            f"{len(new_chunks)} new chunks."
        )

        return {
            "filename": source_name,
            "pages": len(pages),
            "chunks": len(new_chunks),
        }