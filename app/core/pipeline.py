import logging
import time

from app.retrieval.hybrid import HybridSearcher
from app.generation.generator import RAGGenerator


logger = logging.getLogger(__name__)


class RAGPipeline:

    def __init__(self):
        logger.info("Initializing RAG pipeline...")

        self.searcher = HybridSearcher()
        self.generator = RAGGenerator()

        logger.info(
            "RAG pipeline initialized successfully."
        )

    def query(
        self,
        question: str,
        retrieval_limit: int = 5,
    ):
        if not question or not question.strip():
            raise ValueError(
                "Question cannot be empty."
            )

        question = question.strip()

        start_time = time.perf_counter()

        logger.info(
            "Processing query: %s",
            question,
        )

        # -----------------------------------------
        # Retrieval
        # -----------------------------------------

        retrieval_start = time.perf_counter()

        search_result = self.searcher.search(
            query=question,
            limit=retrieval_limit,
        )

        results = search_result["results"]
        retrieval_metadata = search_result["metadata"]

        retrieval_time = (
            time.perf_counter()
            - retrieval_start
        )

        logger.info(
            "Retrieved %d documents in %.3fs",
            len(results),
            retrieval_time,
        )

        # -----------------------------------------
        # No results
        # -----------------------------------------

        if not results:
            total_time = (
                time.perf_counter()
                - start_time
            )

            logger.warning(
                "No relevant documents found."
            )

            return {
                "question": question,
                "answer": (
                    "I could not find relevant information "
                    "in the provided documents."
                ),
                "sources": [],
                "retrieval": retrieval_metadata,
                "metrics": {
                    "retrieval_time": round(
                        retrieval_time,
                        3,
                    ),
                    "generation_time": 0.0,
                    "total_time": round(
                        total_time,
                        3,
                    ),
                },
            }

        # -----------------------------------------
        # Generation
        # -----------------------------------------

        logger.info(
            "Generating answer..."
        )

        generation_start = time.perf_counter()

        answer = self.generator.generate(
            query=question,
            results=results,
        )

        generation_time = (
            time.perf_counter()
            - generation_start
        )

        # -----------------------------------------
        # Sources
        # -----------------------------------------

        sources = []

        for result in results:
            chunk = result["chunk"]

            sources.append(
                {
                    "source": chunk["source"],
                    "page": chunk["page"],
                    "chunk_id": chunk["chunk_id"],
                    "score": result["score"],
                }
            )

        # -----------------------------------------
        # Total time
        # -----------------------------------------

        total_time = (
            time.perf_counter()
            - start_time
        )

        logger.info(
            "Generation completed in %.3fs",
            generation_time,
        )

        logger.info(
            "Total query time: %.3fs",
            total_time,
        )

        # -----------------------------------------
        # Final response
        # -----------------------------------------

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "retrieval": retrieval_metadata,
            "metrics": {
                "retrieval_time": round(
                    retrieval_time,
                    3,
                ),
                "generation_time": round(
                    generation_time,
                    3,
                ),
                "total_time": round(
                    total_time,
                    3,
                ),
            },
        }