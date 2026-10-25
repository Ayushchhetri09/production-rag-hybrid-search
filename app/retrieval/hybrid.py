
from app.retrieval.bm25 import BM25Searcher
from app.retrieval.reranker import Reranker
from app.retrieval.search import SemanticSearcher


class HybridSearcher:
    def __init__(
        self,
        chunks_path: str = "data/processed/chunks.json",
    ):
        self.chunks_path = chunks_path
        self.semantic_searcher = SemanticSearcher()
        self.bm25_searcher = BM25Searcher(chunks_path)
        self.reranker = Reranker()

    def refresh(self):
        """Reload the BM25 index after new documents are added."""
        self.bm25_searcher.reload()
        print("Hybrid searcher refreshed successfully.")

    def search(
        self,
        query: str,
        limit: int = 5,
        dense_limit: int = 20,
        bm25_limit: int = 20,
        rerank_limit: int = 10,
        k: int = 60,
    ):
        # 1. Retrieve candidates from both search systems.
        dense_results = self.semantic_searcher.search(
            query,
            limit=dense_limit,
        )

        bm25_results = self.bm25_searcher.search(
            query,
            limit=bm25_limit,
        )

        # 2. Fuse rankings using Reciprocal Rank Fusion.
        fused_scores = {}
        chunks = {}

        for rank, result in enumerate(dense_results, start=1):
            chunk = result.payload
            chunk_id = chunk["chunk_id"]

            fused_scores[chunk_id] = (
                fused_scores.get(chunk_id, 0)
                + 1 / (k + rank)
            )
            chunks[chunk_id] = chunk

        for rank, result in enumerate(bm25_results, start=1):
            chunk = result["chunk"]
            chunk_id = chunk["chunk_id"]

            fused_scores[chunk_id] = (
                fused_scores.get(chunk_id, 0)
                + 1 / (k + rank)
            )
            chunks[chunk_id] = chunk

        fused_ranked = sorted(
            fused_scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        candidates = []

        for chunk_id, rrf_score in fused_ranked[:rerank_limit]:
            candidates.append(
                {
                    "rrf_score": rrf_score,
                    "chunk": chunks[chunk_id],
                }
            )

        # 3. Rerank the fused candidates.
        reranked = self.reranker.rerank(
            query=query,
            results=candidates,
            limit=limit,
        )

        # 4. Return results and retrieval statistics.
        return {
            "results": reranked,
            "metadata": {
                "dense_candidates": len(dense_results),
                "bm25_candidates": len(bm25_results),
                "rrf_candidates": len(candidates),
                "reranked_results": len(reranked),
            },
        }
