from sentence_transformers import CrossEncoder


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class Reranker:
    def __init__(self, model_name: str = MODEL_NAME):
        self.model = CrossEncoder(model_name)

    def rerank(
        self,
        query: str,
        results: list[dict],
        limit: int = 5,
    ):
        pairs = [
            [query, result["chunk"]["text"]]
            for result in results
        ]

        scores = self.model.predict(pairs)

        reranked = []

        for result, score in zip(results, scores):
            reranked.append(
                {
                    "score": float(score),
                    "chunk": result["chunk"],
                }
            )

        reranked.sort(
            key=lambda x: x["score"],
            reverse=True,
        )

        return reranked[:limit]