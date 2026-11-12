"""Open-source RAG pipeline: ChromaDB (vector store) + sentence-transformers.

Zero paid dependencies. Runs entirely locally. The pipeline is lazy — the
embedding model and vector store are initialized only when first used.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from loguru import logger

from app.core.config import get_settings
from app.rag.knowledge import SEED_DOCUMENTS


class RAGPipeline:
    """Retrieval pipeline backed by ChromaDB and sentence-transformers."""

    def __init__(self) -> None:
        settings = get_settings()
        self._persist_dir = settings.CHROMA_PERSIST_DIR
        self._collection_name = "glymmy_knowledge"
        self._client: Any = None
        self._collection: Any = None
        self._embedder: Any = None
        logger.info(f"RAGPipeline constructed | persist_dir={self._persist_dir}")

    def _ensure_ready(self) -> None:
        if self._collection is not None:
            return

        # Lazy imports — these are heavy
        import chromadb
        from chromadb.config import Settings as ChromaSettings

        settings = get_settings()
        if settings.CHROMA_MODE == "server":
            # Connect to a remote ChromaDB server (Docker Compose / production)
            self._client = chromadb.HttpClient(
                host=settings.CHROMA_HOST.rstrip("/").split("://")[-1].split(":")[0],
                port=int(settings.CHROMA_HOST.rstrip("/").split(":")[-1] or "8000"),
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            logger.info(f"ChromaDB connected in server mode | host={settings.CHROMA_HOST}")
        else:
            # Embedded mode — local file storage (default for dev)
            self._client = chromadb.PersistentClient(
                path=self._persist_dir,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            logger.info(f"ChromaDB running in embedded mode | dir={self._persist_dir}")

        self._collection = self._client.get_or_create_collection(
            name=self._collection_name
        )

        # Seed on first use if empty
        if self._collection.count() == 0:
            logger.info("Seeding RAG knowledge base...")
            self._seed()

    def _seed(self) -> None:
        from sentence_transformers import SentenceTransformer

        self._embedder = self._embedder or SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )
        ids = [d["id"] for d in SEED_DOCUMENTS]
        docs = [d["content"] for d in SEED_DOCUMENTS]
        metas = [
            {"title": d["title"], "source": d["source"]} for d in SEED_DOCUMENTS
        ]
        embeddings = self._embedder.encode(docs).tolist()
        self._collection.add(
            ids=ids, documents=docs, metadatas=metas, embeddings=embeddings
        )
        logger.info(f"Seeded {len(ids)} documents into RAG index")

    def add_document(
        self, doc_id: str, content: str, metadata: dict[str, Any] | None = None
    ) -> None:
        self._ensure_ready()
        from sentence_transformers import SentenceTransformer

        self._embedder = self._embedder or SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )
        embedding = self._embedder.encode([content]).tolist()
        self._collection.add(
            ids=[doc_id],
            documents=[content],
            metadatas=[metadata or {}],
            embeddings=embedding,
        )

    def retrieve(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        """Return the top-k most relevant documents for a query."""
        self._ensure_ready()
        from sentence_transformers import SentenceTransformer

        self._embedder = self._embedder or SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )
        q_embedding = self._embedder.encode([query]).tolist()
        results = self._collection.query(
            query_embeddings=q_embedding,
            n_results=top_k,
        )
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        ids = results.get("ids", [[]])[0]
        distances = results.get("distances", [[]])[0]

        return [
            {
                "id": ids[i],
                "content": docs[i],
                "metadata": metas[i],
                "score": 1 - distances[i] if distances else None,
            }
            for i in range(len(docs))
        ]


@lru_cache
def get_rag_pipeline() -> RAGPipeline:
    """Return the singleton RAG pipeline."""
    return RAGPipeline()
