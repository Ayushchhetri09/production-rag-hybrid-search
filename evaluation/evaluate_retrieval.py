
import json
import sys
from pathlib import Path

# Make the project root importable when this script is run directly.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.retrieval.hybrid import HybridSearcher


DATASET_PATH = PROJECT_ROOT / "evaluation" / "questions.json"
TOP_K = 5


def load_questions():
    """Load and validate the manually labelled evaluation questions."""
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Evaluation dataset not found: {DATASET_PATH}"
        )

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        questions = json.load(file)

    if not isinstance(questions, list) or not questions:
        raise ValueError(
            "questions.json must contain a non-empty JSON list."
        )

    for index, item in enumerate(questions, start=1):
        if not item.get("question", "").strip():
            raise ValueError(f"Question {index} has no question text.")

        if not item.get("relevant_pages"):
            raise ValueError(
                f"Question {index} has no relevant_pages labels."
            )

        for page in item["relevant_pages"]:
            if not page.get("source") or not isinstance(
                page.get("page"), int
            ):
                raise ValueError(
                    f"Question {index} has an invalid source/page label."
                )

    return questions


def evaluate_question(searcher, item):
    """Compare the top retrieved chunks against labelled relevant pages."""
    question = item["question"]
    relevant_pages = {
        (entry["source"], entry["page"])
        for entry in item["relevant_pages"]
    }

    search_output = searcher.search(
        query=question,
        limit=TOP_K,
    )

    # HybridSearcher returns a dictionary containing results and metadata.
    results = search_output["results"]

    retrieved_pages = []
    for result in results[:TOP_K]:
        chunk = result["chunk"]
        retrieved_pages.append(
            (chunk["source"], chunk["page"])
        )

    relevant_ranks = [
        rank
        for rank, page in enumerate(retrieved_pages, start=1)
        if page in relevant_pages
    ]

    hit = 1.0 if relevant_ranks else 0.0
    reciprocal_rank = (
        1.0 / relevant_ranks[0] if relevant_ranks else 0.0
    )

    # Count distinct relevant pages retrieved.
    recall = (
        len(set(retrieved_pages) & relevant_pages)
        / len(relevant_pages)
    )

    return {
        "question": question,
        "hit_at_5": hit,
        "mrr_at_5": reciprocal_rank,
        "recall_at_5": recall,
        "retrieved_pages": retrieved_pages,
    }


def main():
    questions = load_questions()

    print(f"Loaded {len(questions)} evaluation questions.")
    print("Initializing hybrid searcher...")
    searcher = HybridSearcher()

    evaluations = []

    for index, item in enumerate(questions, start=1):
        print(f"\nEvaluating question {index}/{len(questions)}...")
        result = evaluate_question(searcher, item)
        evaluations.append(result)

        print(f"Question: {result['question']}")
        print(f"Hit@5:    {result['hit_at_5']:.2f}")
        print(f"MRR@5:    {result['mrr_at_5']:.2f}")
        print(f"Recall@5: {result['recall_at_5']:.2f}")

        if result["retrieved_pages"]:
            print("Retrieved pages:")
            for source, page in result["retrieved_pages"]:
                print(f"  - {source}, page {page}")
        else:
            print("No results retrieved.")

    count = len(evaluations)
    summary = {
        "questions_evaluated": count,
        "hit_at_5": sum(
            result["hit_at_5"] for result in evaluations
        ) / count,
        "mrr_at_5": sum(
            result["mrr_at_5"] for result in evaluations
        ) / count,
        "recall_at_5": sum(
            result["recall_at_5"] for result in evaluations
        ) / count,
    }

    output = {
        "summary": summary,
        "results": evaluations,
    }

    output_path = PROJECT_ROOT / "evaluation" / "evaluation_results.json"
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(output, file, indent=2, ensure_ascii=False)

    print("\n========== EVALUATION SUMMARY ==========")
    print(f"Questions: {summary['questions_evaluated']}")
    print(f"Mean Hit@5:    {summary['hit_at_5']:.3f}")
    print(f"Mean MRR@5:    {summary['mrr_at_5']:.3f}")
    print(f"Mean Recall@5: {summary['recall_at_5']:.3f}")
    print(f"\nDetailed results saved to: {output_path}")


if __name__ == "__main__":
    main()
