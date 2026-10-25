from pathlib import Path
import json
import shutil
import tempfile

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.core.pipeline import RAGPipeline
from app.ingestion.document_ingestion import DocumentIngestionService


app = FastAPI(
    title="Production RAG with Hybrid Search",
    description=(
        "A production-oriented RAG API using hybrid retrieval, "
        "reranking, and Gemini."
    ),
    version="1.0.0",
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Initialize RAG pipeline
# --------------------------------------------------

pipeline = RAGPipeline()


# Reuse the same embedding model and Qdrant store
# already created by the semantic searcher.
ingestion_service = DocumentIngestionService(
    embedding_model=pipeline.searcher.semantic_searcher.embedding_model,
    qdrant_store=pipeline.searcher.semantic_searcher.store,
)


class QueryRequest(BaseModel):
    question: str


# --------------------------------------------------
# Root
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Production RAG API is running."
    }


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/documents")
def documents():
    chunks_path = Path(
        "data/processed/chunks.json"
    )

    if not chunks_path.exists():
        return {
            "documents": []
        }

    with chunks_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        chunks = json.load(file)

    documents = {}

    for chunk in chunks:
        source = chunk["source"]

        if source not in documents:
            documents[source] = {
                "filename": source,
                "pages": set(),
                "chunks": 0,
            }

        documents[source]["pages"].add(
            chunk["page"]
        )

        documents[source]["chunks"] += 1

    result = []

    for document in documents.values():
        result.append(
            {
                "filename": document["filename"],
                "pages": len(document["pages"]),
                "chunks": document["chunks"],
            }
        )

    return {
        "documents": result
    }


# --------------------------------------------------
# Query endpoint
# --------------------------------------------------

@app.post("/query")
def query(request: QueryRequest):
    try:
        result = pipeline.query(
            question=request.question
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except RuntimeError as e:
        error_message = str(e)

        if (
            "quota" in error_message.lower()
            or "429" in error_message
        ):
            raise HTTPException(
                status_code=429,
                detail=error_message,
            )

        raise HTTPException(
            status_code=503,
            detail=error_message,
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred.",
        )


# --------------------------------------------------
# PDF upload endpoint
# --------------------------------------------------

@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...)
):
    # Check file extension
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file was provided.",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    temp_path = None

    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
        ) as temp_file:

            temp_path = Path(temp_file.name)

            shutil.copyfileobj(
                file.file,
                temp_file,
            )

        # Process the uploaded PDF
        result = ingestion_service.ingest_pdf(
    str(temp_path),
    source_name=file.filename,
)

        # Use the original filename in the response
        result["filename"] = file.filename

        # Refresh BM25 so the new document
        # participates in hybrid search.
        pipeline.searcher.refresh()

        return {
            "message": "PDF uploaded and indexed successfully.",
            **result,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except Exception as e:
        print(
            f"Upload error: {type(e).__name__}: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to process the PDF.",
        )

    finally:
        # Delete temporary uploaded file
        if temp_path and temp_path.exists():
            temp_path.unlink()
