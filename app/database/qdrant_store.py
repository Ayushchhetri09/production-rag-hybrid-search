from pathlib import Path
import hashlib

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams


COLLECTION_NAME = "documents"
VECTOR_SIZE = 384

QDRANT_PATH = Path("data/qdrant")


class QdrantStore:
    def __init__(
        self,
        path: str = str(QDRANT_PATH),
        collection_name: str = COLLECTION_NAME,
    ):
        self.client = QdrantClient(path=path)
        self.collection_name = collection_name

        self._create_collection()

    def _create_collection(self):
        collections = self.client.get_collections().collections

        existing_names = {
            collection.name for collection in collections
        }

        if self.collection_name not in existing_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            )

    def upsert(
        self,
        embeddings,
        chunks: list[dict],
    ):
        points = []

        for embedding, chunk in zip(embeddings, chunks):

            # Create a stable unique ID from the chunk ID
            chunk_id = chunk["chunk_id"]

            point_id = hashlib.md5(
                chunk_id.encode("utf-8")
            ).hexdigest()

            # Qdrant accepts integer or UUID IDs.
            # Convert the MD5 hash into a valid UUID-like value.
            point_id = (
                f"{point_id[:8]}-"
                f"{point_id[8:12]}-"
                f"{point_id[12:16]}-"
                f"{point_id[16:20]}-"
                f"{point_id[20:]}"
            )

            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding.tolist(),
                    payload=chunk,
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

        print(
            f"Upserted {len(points)} chunks into Qdrant."
        )

    def search(
        self,
        query_vector,
        limit: int = 5,
    ):
        return self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector.tolist(),
            limit=limit,
        ).points