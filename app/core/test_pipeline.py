from app.core.pipeline import RAGPipeline


def main():
    pipeline = RAGPipeline()

    question = "What does Thoreau say about living deliberately?"

    result = pipeline.query(question)

    print("\n" + "=" * 60)
    print("QUESTION")
    print("=" * 60)
    print(result["question"])

    print("\n" + "=" * 60)
    print("ANSWER")
    print("=" * 60)
    print(result["answer"])

    print("\n" + "=" * 60)
    print("SOURCES")
    print("=" * 60)

    for source in result["sources"]:
        print(
            f"- {source['source']} "
            f"(Page {source['page']}) "
            f"[Score: {source['score']:.4f}]"
        )


if __name__ == "__main__":
    main()