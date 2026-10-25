# Production RAG with Hybrid Search

A Retrieval-Augmented Generation (RAG) application that combines semantic search, keyword-based retrieval, result fusion, and reranking to answer questions from documents with relevant source references.

The project explores how retrieval quality can be improved by combining complementary search methods rather than relying on vector similarity alone.

## Overview

Traditional keyword search can miss semantically similar passages, while semantic search can overlook exact terms and specific phrases. This project combines both approaches to retrieve relevant document chunks before generating an answer with a large language model.

The application includes a Python backend and a React frontend, with local Qdrant storage for document embeddings and retrieval.

## Key Features

- **Hybrid retrieval:** Combines semantic retrieval with BM25 keyword search.
- **Result fusion:** Uses Reciprocal Rank Fusion (RRF) to combine rankings from different retrieval methods.
- **Reranking:** Reorders retrieved passages to improve relevance.
- **RAG answer generation:** Uses the Gemini API to generate answers grounded in retrieved context.
- **Source references:** Returns source document names, page numbers, and relevance scores.
- **PDF ingestion:** Extracts document content and splits it into chunks for retrieval.
- **Interactive frontend:** Provides a web interface for asking questions and viewing answers.
- **Retrieval evaluation:** Includes scripts and question sets for examining retrieval performance.

## Architecture

1. **Document ingestion:** Extract text from PDF documents.
2. **Chunking:** Split extracted text into smaller passages.
3. **Indexing:** Generate embeddings and store document chunks in Qdrant; prepare keyword-based retrieval data.
4. **Hybrid retrieval:** Retrieve candidate passages using semantic search and BM25.
5. **Rank fusion:** Combine candidate rankings using Reciprocal Rank Fusion.
6. **Reranking:** Reorder retrieved passages based on relevance.
7. **Generation:** Send the question and retrieved context to Gemini.
8. **Response:** Return the generated answer and relevant source references to the frontend.

## Tech Stack

## Tech Stack

- **Language:** Python 3.13
- **Backend:** FastAPI
- **Frontend:** React, Vite, JavaScript, CSS
- **Vector database:** Qdrant (local storage)
- **Embeddings:** Sentence Transformers with pretrained models from the Hugging Face ecosystem
- **Retrieval:** Semantic search, BM25, Reciprocal Rank Fusion (RRF)
- **Reranking:** Cross-encoder reranking using pretrained models
- **LLM:** Google Gemini API
- **Model ecosystem:** Hugging Face Hub for pretrained model access and downloads
- **Testing and evaluation:** Python scripts, pytest, and retrieval evaluation metrics


## Example

**Question:** What does Thoreau say about living deliberately?

**Answer:** Thoreau emphasizes that people should act deliberately and choose activities they can consciously justify to themselves.

**Retrieved source:** *Walden* by Henry David Thoreau, page 27.

The application returns multiple relevant source passages alongside the generated answer.

## Project Structure

```text
production-rag-hybrid-search/
├── app/
│   ├── api/             # API endpoints and request/response schemas
│   ├── core/            # RAG pipeline and logging
│   ├── database/        # Qdrant storage integration
│   ├── generation/      # Gemini answer generation
│   ├── ingestion/       # PDF loading, chunking, and storage
│   └── retrieval/       # Embeddings, BM25, hybrid search, reranking
├── evaluation/          # Retrieval evaluation scripts and datasets
├── frontend/            # React application
├── data/                # Local documents and vector database (not committed)
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
└── .gitignore
```

## Getting Started

### Prerequisites

- Python 3.13
- Node.js and npm
- A Google Gemini API key
- The documents you want to index

### 1. Clone the repository

```bash
git clone https://github.com/Ayushchhetri09/production-rag-hybrid-search.git
cd production-rag-hybrid-search
```

### 2. Set up Python

Create and activate a virtual environment.

**Windows PowerShell:**

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root using `.env.example` as a template.

```env
GEMINI_API_KEY=your_gemini_api_key
```

Replace the placeholder with your own API key. Never commit your `.env` file or expose your API key publicly.

### 4. Prepare the documents

Place your PDF documents in the directory expected by the ingestion code. Run the ingestion and indexing commands implemented in the project to extract text, create chunks, generate embeddings, and populate Qdrant.

### 5. Start the backend

Activate the virtual environment, then run the FastAPI application using the module and command configured in `app/api/main.py`.

For example, if the FastAPI instance is named `app` in that module:

```powershell
python -m uvicorn app.api.main:app --reload
```

### 6. Start the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite in your browser.

> Note: Confirm that the backend and frontend API URLs, document-ingestion command, and required environment variables match your current implementation.

## Evaluation

The repository includes retrieval evaluation scripts and a question set to help assess whether relevant passages appear among the retrieved results.

Evaluation should consider metrics such as:

- **Recall@K:** Whether relevant passages appear within the top K retrieved results.
- **MRR:** How highly the first relevant result is ranked.
- **Latency:** How long retrieval takes for a query.

The current evaluation dataset is small and should be treated as an initial experiment, not conclusive evidence of general retrieval performance. A larger, carefully labelled dataset is needed for reliable comparisons.

## Limitations

- Retrieval quality depends on document extraction, chunk size, embedding quality, and query wording.
- Generation quality depends on the relevance of retrieved context and the underlying language model.
- Local Qdrant storage is intended for local development and is not configured here as a shared production database.
- Automated pytest coverage is still a work in progress.

## Future Improvements

- Add automated unit and integration tests.
- Expand the labelled retrieval evaluation dataset.
- Compare semantic-only, BM25-only, and hybrid retrieval.
- Measure Recall@K, MRR, and retrieval latency.
- Add response streaming and improved error handling.
- Add Docker-based deployment and production database configuration.
- Improve observability with structured logs and request-level metrics.

## Author

**Ayush Chhetri**  
Electrical Engineering, NIT Silchar

GitHub: [Ayushchhetri09](https://github.com/Ayushchhetri09)
