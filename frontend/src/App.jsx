import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [retrieval, setRetrieval] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [history, setHistory] = useState([]);

  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [uploadError, setUploadError] = useState("");

  const [documents, setDocuments] = useState([]);
  const [documentsLoading, setDocumentsLoading] = useState(true);

  async function loadDocuments() {
  try {
    const response = await fetch(
      `${API_URL}/documents`
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Unable to load documents."
      );
    }

    setDocuments(data.documents || []);
  } catch (err) {
    console.error(
      "Failed to load documents:",
      err
    );
  } finally {
    setDocumentsLoading(false);
  }
}

useEffect(() => {
  loadDocuments();
}, []);

  async function handleSubmit(e) {
    e.preventDefault();

    if (!question.trim() || loading) {
      return;
    }

    setLoading(true);
    setError("");
    setAnswer("");
    setSources([]);
    setMetrics(null);

    try {
      const response = await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question.trim(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Something went wrong.");
      }

      setAnswer(data.answer || "");
      setSources(data.sources || []);
      setMetrics(data.metrics || null);
      setRetrieval(data.retrieval || null);

      setHistory((prev) => [
  ...prev,
  {
    question: question.trim(),
    answer: data.answer || "",
    sources: data.sources || [],
    metrics: data.metrics || null,
    retirieval: data.retrieval || null,
  },
]);
    } catch (err) {
      setError(
        err.message || "Unable to connect to the RAG backend."
      );
    } finally {
      setLoading(false);
    }
  }
  async function handleUpload(e) {
  const file = e.target.files[0];

  if (!file) {
    return;
  }

  if (!file.name.toLowerCase().endsWith(".pdf")) {
    setUploadError("Only PDF files are supported.");
    setUploadMessage("");
    return;
  }

  setUploading(true);
  setUploadMessage("");
  setUploadError("");

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch(`${API_URL}/upload`, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "PDF upload failed."
      );
    }

    setUploadMessage(
      `${data.filename} uploaded successfully.`
    );

    await loadDocuments();
  } catch (err) {
    setUploadError(
      err.message || "Unable to upload the PDF."
    );
  } finally {
    setUploading(false);
    e.target.value = "";
  }
}

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="brand">
            <div className="brand-icon">R</div>

            <div>
              <h1>Production RAG</h1>
              <p>Hybrid Search • Reranking • Gemini</p>
            </div>
          </div>

          <div className="header-actions">
  <div className="status">
    <span className="status-dot"></span>
    API Ready
  </div>

  {history.length > 0 && (
    <button
      className="new-chat"
      type="button"
      onClick={() => {
        setHistory([]);
        setQuestion("");
        setAnswer("");
        setSources([]);
        setMetrics(null);
        setRetrieval(null);
        setError("");
      }}
    >
      + New Chat
    </button>
  )}
</div>
        </div>
      </header>

      <main className="main">
        <section className="hero">
          <div className="hero-badge">
            AI DOCUMENT ASSISTANT
          </div>

          <h2>Ask your documents.</h2>

          <p>
            Get accurate answers grounded in your indexed
            documents using hybrid search and AI reranking.
          </p>
        </section>

       <div className="upload-card">
  <div className="upload-icon">
    📄
  </div>

  <div className="upload-content">
    <h3>Upload your PDF</h3>

    <p>
      Add a document to your RAG knowledge base
      and start asking questions about it.
    </p>

    <span className="upload-format">
      PDF files only
    </span>

    <label className="upload-button">
      {uploading ? "Uploading..." : "Upload PDF"}

      <input
        type="file"
        accept=".pdf,application/pdf"
        onChange={handleUpload}
        disabled={uploading}
        hidden
      />
    </label>

    <span className="upload-hint">
      Click "Upload PDF" to choose a document
    </span>
  </div>
</div>

{uploadMessage && (
  <div className="upload-success">
    ✓ {uploadMessage}
  </div>
)}

{uploadError && (
  <div className="upload-error">
    ✕ {uploadError}
  </div>
)}

<section className="knowledge-base">
  <div className="knowledge-header">
    <div>
      <h3>Knowledge Base</h3>
      <p>Documents currently indexed for retrieval.</p>
    </div>

    <span className="document-count">
      {documents.length}{" "}
      {documents.length === 1 ? "document" : "documents"}
    </span>
  </div>

  {documentsLoading ? (
    <div className="knowledge-empty">
      Loading documents...
    </div>
  ) : documents.length === 0 ? (
    <div className="knowledge-empty">
      No documents have been indexed yet.
    </div>
  ) : (
    <div className="document-list">
      {documents.map((document) => (
        <div
          className="document-item"
          key={document.filename}
        >
          <div className="document-icon">
            📄
          </div>

          <div className="document-info">
            <strong>{document.filename}</strong>

            <span>
              {document.pages}{" "}
              {document.pages === 1 ? "page" : "pages"}{" "}
              •{" "}
              {document.chunks}{" "}
              {document.chunks === 1 ? "chunk" : "chunks"}
            </span>
          </div>

          <div className="document-status">
            Indexed
          </div>
        </div>
      ))}
    </div>
  )}
</section>

        <form className="query-card" onSubmit={handleSubmit}>
          <label htmlFor="question">
            Your question
          </label>

          <textarea
            id="question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="What does Thoreau say about living deliberately?"
            rows={4}
            disabled={loading}
          />

          <div className="query-footer">
            <span className="hint">
              Answers are generated from your indexed documents.
            </span>

            <button
              type="submit"
              disabled={loading || !question.trim()}
            >
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Searching...
                </>
              ) : (
                <>
                  Ask Question
                  <span className="arrow">→</span>
                </>
              )}
            </button>
          </div>
        </form>

        {error && (
          <div className="error-card">
            <strong>Request failed</strong>
            <p>{error}</p>
          </div>
        )}

        {history.length > 0 && (
  <section className="history">
    {history.map((item, index) => (
      <div className="conversation" key={index}>
        {/* QUESTION */}
        <div className="question-message">
          <div className="message-label">
            <span className="message-icon">You</span>
            <span>Your question</span>
          </div>

          <p>{item.question}</p>
        </div>
        {/* ANSWER */}
        <div className="result-card">
          <div className="section-title">
            <span className="section-icon">✦</span>
            <h3>Answer</h3>
          </div>

          <div className="answer">
            {item.answer}
          </div>
          {/* SOURCES */}
          {item.sources.length > 0 && (
            <div className="sources-section">
              <div className="section-title source-title">
                <span className="section-icon">◈</span>
                <h3>Sources</h3>

                <span className="source-count">
                  {item.sources.length} sources
                </span>
              </div>

              <div className="sources">
                {item.sources.map((source, sourceIndex) => (
                  <div
                    className="source"
                    key={source.chunk_id || sourceIndex}
                  >
                    <div className="source-number">
                      {sourceIndex + 1}
                    </div>

                    <div className="source-info">
                      <strong>{source.source}</strong>

                      <span>
                        Page {source.page}
                      </span>
                    </div>

                    <div className="score">
                      {typeof source.score === "number"
                        ? source.score.toFixed(3)
                        : "—"}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
{/* RETRIEVAL DETAILS */}
{item.retrieval && (
  <div className="metrics-card retrieval-details">
    <div className="metric">
      <span>Dense Candidates</span>
      <strong>{item.retrieval.dense_candidates}</strong>
    </div>

    <div className="metric">
      <span>BM25 Candidates</span>
      <strong>{item.retrieval.bm25_candidates}</strong>
    </div>

    <div className="metric">
      <span>RRF Candidates</span>
      <strong>{item.retrieval.rrf_candidates}</strong>
    </div>

    <div className="metric">
      <span>Reranked Results</span>
      <strong>{item.retrieval.reranked_results}</strong>
    </div>
  </div>
)}
          {/* METRICS */}
          {item.metrics && (
            <div className="metrics-card">
              <div className="metric">
                <span>Retrieval</span>
                <strong>
                  {item.metrics.retrieval_time}s
                </strong>
              </div>

              <div className="metric">
                <span>Generation</span>
                <strong>
                  {item.metrics.generation_time}s
                </strong>
              </div>

              <div className="metric">
                <span>Total latency</span>
                <strong>
                  {item.metrics.total_time}s
                </strong>
              </div>
            </div>
          )}
        </div>
      </div>
    ))}
  </section>
)}
      </main>

      <footer>
        <p>
          Production RAG with Hybrid Search
        </p>

        <span>
          Semantic Search + BM25 + RRF + Cross-Encoder + Gemini
        </span>
      </footer>
    </div>
  );
}
export default App;