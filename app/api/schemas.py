from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Question to ask the RAG system.",
    )


class Source(BaseModel):
    source: str
    page: int
    chunk_id: str
    score: float


class Metrics(BaseModel):
    retrieval_time: float
    generation_time: float
    total_time: float


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source]
    metrics: Metrics