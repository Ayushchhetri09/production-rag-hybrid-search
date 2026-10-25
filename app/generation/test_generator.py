from app.retrieval.hybrid import HybridSearcher
from app.generation.generator import RAGGenerator


def main():

    query = "What does Thoreau say about living deliberately?"

    print("Retrieving relevant documents...\n")

    searcher = HybridSearcher()

    results = searcher.search(
        query=query,
        limit=5,
    )

    print("Generating answer...\n")

    generator = RAGGenerator()

    answer = generator.generate(
        query=query,
        results=results,
    )

    print("=" * 80)
    print("QUESTION")
    print(query)

    print("\n" + "=" * 80)
    print("ANSWER")
    print(answer)

    print("\n" + "=" * 80)
    print("SOURCES")

    for result in results:
        chunk = result["chunk"]

        print(
            f"- {chunk['source']} "
            f"(Page {chunk['page']})"
        )


if __name__ == "__main__":
    main()