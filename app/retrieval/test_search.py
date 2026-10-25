from app.retrieval.search import SemanticSearcher


def main():
    searcher = SemanticSearcher()

    query = "What does Thoreau say about living deliberately?"

    print(f"Query: {query}\n")

    results = searcher.search(query, limit=5)

    for rank, result in enumerate(results, start=1):
        print("=" * 80)
        print(f"Rank: {rank}")
        print(f"Score: {result.score:.4f}")
        print(f"Source: {result.payload['source']}")
        print(f"Page: {result.payload['page']}")
        print(f"Chunk ID: {result.payload['chunk_id']}")
        print(f"\nText:\n{result.payload['text'][:1000]}")
        print()


if __name__ == "__main__":
    main()