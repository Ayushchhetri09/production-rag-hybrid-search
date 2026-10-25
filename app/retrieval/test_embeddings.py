import json

from app.retrieval.embeddings import EmbeddingModel


CHUNKS_PATH = "data/processed/chunks.json"


def main():
    with open(CHUNKS_PATH, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    texts = [chunk["text"] for chunk in chunks]

    print(f"Loaded {len(texts)} chunks.")

    embedding_model = EmbeddingModel()

    embeddings = embedding_model.encode(texts)

    print(f"Embedding shape: {embeddings.shape}")
    print(f"First embedding dimensions: {embeddings[0][:10]}")


if __name__ == "__main__":
    main()