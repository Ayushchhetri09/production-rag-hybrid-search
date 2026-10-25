import json
import re

from rank_bm25 import BM25Okapi


class BM25Searcher:
    def __init__(self, chunks_path: str):
        self.chunks_path = chunks_path
        self._load_chunks()

    def _load_chunks(self):
        """Load chunks and rebuild the BM25 index."""

        with open(
            self.chunks_path,
            "r",
            encoding="utf-8",
        ) as file:
            self.chunks = json.load(file)

        self.tokenized_documents = [
            self._tokenize(chunk["text"])
            for chunk in self.chunks
        ]

        if self.tokenized_documents:
         self.bm25 = BM25Okapi(
        self.tokenized_documents
    )
        else:
         self.bm25 = None

        print(
            f"BM25 index loaded with "
            f"{len(self.chunks)} chunks."
        )

    def reload(self):
        """Reload chunks and rebuild the BM25 index."""

        self._load_chunks()

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(
            r"\b\w+\b",
            text.lower(),
        )

    def search(
        self,
        query: str,
        limit: int = 5,
    ):
        query_tokens = self._tokenize(query)

        scores = self.bm25.get_scores(
            query_tokens
        )
        if not self.chunks:
         return []

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True,
        )[:limit]

        results = []

        for index in ranked_indices:
            results.append(
                {
                    "score": float(scores[index]),
                    "chunk": self.chunks[index],
                }
            )

        return results