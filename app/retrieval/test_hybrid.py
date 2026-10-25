from app.retrieval.hybrid import HybridSearcher


def main():
    searcher = HybridSearcher()

    query = "What does Thoreau say about living deliberately?"

    print(f"Query: {query}\n")

    results = searcher.search(
        query=query,
        limit=5,
    )

    for rank, result in enumerate(results, start=1):
        chunk = result["chunk"]

        print("=" * 80)
        print(f"Rank: {rank}")
        print(f"Reranker Score: {result['score']:.4f}")
        print(f"Source: {chunk['source']}")
        print(f"Page: {chunk['page']}")
        print(f"Chunk ID: {chunk['chunk_id']}")
        print(f"\nText:\n{chunk['text'][:1000]}")
        print()


if __name__ == "__main__":
    main()