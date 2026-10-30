
import pytest
from pydantic import ValidationError

from app.api.schemas import QueryRequest, Source, Metrics, QueryResponse


def test_query_request_accepts_valid_question():
    request = QueryRequest(question="What is hybrid search?")

    assert request.question == "What is hybrid search?"


def test_query_request_rejects_empty_question():
    with pytest.raises(ValidationError):
        QueryRequest(question="")


def test_query_request_rejects_question_over_2000_characters():
    with pytest.raises(ValidationError):
        QueryRequest(question="a" * 2001)


def test_source_accepts_valid_data():
    source = Source(
        source="Walden.pdf",
        page=27,
        chunk_id="walden-p27-c1",
        score=5.78,
    )

    assert source.source == "Walden.pdf"
    assert source.page == 27
    assert source.score == 5.78


def test_metrics_accept_valid_times():
    metrics = Metrics(
        retrieval_time=0.15,
        generation_time=1.8,
        total_time=1.95,
    )

    assert metrics.total_time == 1.95


def test_query_response_accepts_valid_data():
    response = QueryResponse(
        question="What does Thoreau say about living deliberately?",
        answer="Thoreau emphasizes living intentionally.",
        sources=[
            Source(
                source="Walden.pdf",
                page=27,
                chunk_id="walden-p27-c1",
                score=5.78,
            )
        ],
        metrics=Metrics(
            retrieval_time=0.15,
            generation_time=1.8,
            total_time=1.95,
        ),
    )

    assert response.question.startswith("What does Thoreau")
    assert len(response.sources) == 1
    assert response.metrics.total_time == 1.95
