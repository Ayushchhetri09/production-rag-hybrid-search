from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class EmbeddingModel:
    def __init__(self, model_name: str = MODEL_NAME):
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]):
        return self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
        )