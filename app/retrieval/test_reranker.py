from app.retrieval.reranker import Reranker


def main():
    reranker = Reranker()

    query = "What does Thoreau say about living deliberately?"

    documents = [
        {
            "chunk": {
                "text": (
                    "Acting deliberately was crucial to Thoreau. "
                    "Live thus deliberately for the most part."
                )
            }
        },
        {
            "chunk": {
                "text": (
                    "Thoreau moved to Walden Pond and lived "
                    "in a small cabin in the woods."
                )
            }
        },
    ]

    results = reranker.rerank(
        query=query,
        results=documents,
        limit=2,
    )

    for rank, result in enumerate(results, start=1):
        print("=" * 60)
        print(f"Rank: {rank}")
        print(f"Score: {result['score']:.4f}")
        print(f"Text: {result['chunk']['text']}")


if __name__ == "__main__":
    main()