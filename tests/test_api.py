
import importlib
import sys
from unittest.mock import patch

from fastapi.testclient import TestClient


class FakePipeline:
    """Mock pipeline so tests never load models or connect to Qdrant."""

    def __init__(self):
        self.searcher = type(
            "Searcher",
            (),
            {
                "semantic_searcher": type(
                    "SemanticSearcher",
                    (),
                    {
                        "embedding_model": object(),
                        "store": object(),
                    },
                )(),
                "refresh": lambda self: None,
            },
        )()

    def query(self, question):
        if question == "raise-value-error":
            raise ValueError("Invalid question")

        if question == "raise-quota-error":
            raise RuntimeError("API quota exceeded")

        if question == "raise-runtime-error":
            raise RuntimeError("Service unavailable")

        return {
            "question": question,
            "answer": "This is a mocked answer.",
            "sources": [],
            "metrics": {
                "retrieval_time": 0.1,
                "generation_time": 0.5,
                "total_time": 0.6,
            },
        }


class FakeIngestionService:
    def __init__(self, **kwargs):
        pass


# Replace expensive services before importing the API module.
with (
    patch(
        "app.core.pipeline.RAGPipeline",
        FakePipeline,
    ),
    patch(
        "app.ingestion.document_ingestion.DocumentIngestionService",
        FakeIngestionService,
    ),
):
    sys.modules.pop("app.api.main", None)
    api = importlib.import_module("app.api.main")


client = TestClient(api.app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Production RAG API is running."
    }


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_query_endpoint_success():
    response = client.post(
        "/query",
        json={"question": "What is hybrid search?"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["question"] == "What is hybrid search?"
    assert data["answer"] == "This is a mocked answer."
    assert data["sources"] == []
    assert data["metrics"]["total_time"] == 0.6


def test_query_endpoint_rejects_missing_question():
    response = client.post("/query", json={})

    assert response.status_code == 422


def test_query_endpoint_handles_value_error():
    response = client.post(
        "/query",
        json={"question": "raise-value-error"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid question"


def test_query_endpoint_handles_quota_error():
    response = client.post(
        "/query",
        json={"question": "raise-quota-error"},
    )

    assert response.status_code == 429


def test_query_endpoint_handles_runtime_error():
    response = client.post(
        "/query",
        json={"question": "raise-runtime-error"},
    )

    assert response.status_code == 503


def test_upload_rejects_non_pdf():
    response = client.post(
        "/upload",
        files={
            "file": (
                "notes.txt",
                b"This is not a PDF.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Only PDF files are supported."
    )