from app.database.qdrant_store import QdrantStore
from app.retrieval.embeddings import EmbeddingModel


class SemanticSearcher:
    def __init__(self):
        self.embedding_model = EmbeddingModel()
        self.store = QdrantStore()

    def search(self, query: str, limit: int = 5):
        query_embedding = self.embedding_model.encode([query])[0]

        results = self.store.search(
            query_vector=query_embedding,
            limit=limit,
        )

        return results