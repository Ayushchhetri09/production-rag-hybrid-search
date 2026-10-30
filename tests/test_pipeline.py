
from unittest.mock import Mock, patch

import pytest

from app.core.pipeline import RAGPipeline


@pytest.fixture
def pipeline():
    """Create a pipeline without initializing real models or Qdrant."""
    with (
        patch("app.core.pipeline.HybridSearcher"),
        patch("app.core.pipeline.RAGGenerator"),
    ):
        instance = RAGPipeline()

    instance.searcher = Mock()
    instance.generator = Mock()

    return instance


def sample_result():
    return {
        "results": [
            {
                "chunk": {
                    "source": "Walden.pdf",
                    "page": 27,
                    "chunk_id": "walden-p27-c1",
                    "text": "Thoreau emphasizes living deliberately.",
                },
                "score": 5.78,
            }
        ],
        "metadata": {
            "retrieval_method": "hybrid",
        },
    }


def test_query_retrieves_documents_and_generates_answer(pipeline):
    pipeline.searcher.search.return_value = sample_result()
    pipeline.generator.generate.return_value = (
        "Thoreau emphasizes living deliberately."
    )

    response = pipeline.query(
        "  What does Thoreau say?  "
    )

    pipeline.searcher.search.assert_called_once_with(
        query="What does Thoreau say?",
        limit=5,
    )

    pipeline.generator.generate.assert_called_once()

    assert response["question"] == "What does Thoreau say?"
    assert response["answer"] == (
        "Thoreau emphasizes living deliberately."
    )
    assert len(response["sources"]) == 1
    assert response["sources"][0]["source"] == "Walden.pdf"
    assert response["sources"][0]["page"] == 27
    assert response["sources"][0]["chunk_id"] == "walden-p27-c1"
    assert response["sources"][0]["score"] == 5.78


def test_query_passes_custom_retrieval_limit(pipeline):
    pipeline.searcher.search.return_value = sample_result()
    pipeline.generator.generate.return_value = "Example answer."

    pipeline.query("Example question", retrieval_limit=3)

    pipeline.searcher.search.assert_called_once_with(
        query="Example question",
        limit=3,
    )


def test_query_without_results_skips_generation(pipeline):
    pipeline.searcher.search.return_value = {
        "results": [],
        "metadata": {"retrieval_method": "hybrid"},
    }

    response = pipeline.query("Unknown topic")

    pipeline.generator.generate.assert_not_called()

    assert response["question"] == "Unknown topic"
    assert response["sources"] == []
    assert "could not find relevant information" in (
        response["answer"].lower()
    )
    assert response["metrics"]["generation_time"] == 0.0


@pytest.mark.parametrize(
    "question",
    ["", "   ", "\t\n"],
)
def test_query_rejects_empty_or_whitespace_question(
    pipeline,
    question,
):
    with pytest.raises(
        ValueError,
        match="Question cannot be empty",
    ):
        pipeline.query(question)

    pipeline.searcher.search.assert_not_called()
    pipeline.generator.generate.assert_not_called()