import json

from app.database.qdrant_store import QdrantStore
from app.retrieval.embeddings import EmbeddingModel


CHUNKS_PATH = "data/processed/chunks.json"


def main():
    with open(CHUNKS_PATH, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    print(f"Loaded {len(chunks)} chunks.")

    texts = [chunk["text"] for chunk in chunks]

    embedding_model = EmbeddingModel()

    embeddings = embedding_model.encode(texts)

    print(f"Generated embeddings: {embeddings.shape}")

    store = QdrantStore()

    store.upsert(
        embeddings=embeddings,
        chunks=chunks,
    )

    print("Successfully indexed documents into Qdrant.")


if __name__ == "__main__":
    main()