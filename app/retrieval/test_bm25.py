from app.retrieval.bm25 import BM25Searcher


def main():
    searcher = BM25Searcher(
        "data/processed/chunks.json"
    )

    query = "What does Thoreau say about living deliberately?"

    print(f"Query: {query}\n")

    results = searcher.search(query, limit=5)

    for rank, result in enumerate(results, start=1):
        chunk = result["chunk"]

        print("=" * 80)
        print(f"Rank: {rank}")
        print(f"Score: {result['score']:.4f}")
        print(f"Source: {chunk['source']}")
        print(f"Page: {chunk['page']}")
        print(f"Chunk ID: {chunk['chunk_id']}")
        print(f"\nText:\n{chunk['text'][:1000]}")
        print()


if __name__ == "__main__":
    main()