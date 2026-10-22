"""
retriever.py
============
Top-K similarity retrieval with optional score filtering.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from .embeddings import EmbeddingModel
from .vectorstore import FAISSVectorStore, VectorStoreError

logger = logging.getLogger(__name__)


class Retriever:
    """
    Combines an embedding model and a FAISS vector store to retrieve the
    most relevant chunks for a given natural-language query.
    """

    def __init__(
        self,
        vector_store: FAISSVectorStore,
        embedding_model: EmbeddingModel,
        top_k: int = 5,
        score_threshold: Optional[float] = None,
    ) -> None:
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.top_k = top_k
        self.score_threshold = score_threshold

    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        """Retrieve the most relevant chunks for `query` as a list of dicts."""
        if not query or not query.strip():
            logger.warning("Empty query passed to retriever.")
            return []

        k = top_k or self.top_k

        try:
            query_embedding = self.embedding_model.embed_query(query)
            results = self.vector_store.search(query_embedding, top_k=k)
        except VectorStoreError as exc:
            logger.warning("Retrieval failed: %s", exc)
            return []

        retrieved = []
        for metadata, score in results:
            if self.score_threshold is not None and score < self.score_threshold:
                continue
            retrieved.append(
                {
                    "text": metadata.text,
                    "source": metadata.source,
                    "chunk_id": metadata.chunk_id,
                    "score": round(score, 4),
                }
            )

        logger.info("Retrieved %d chunks for query: '%s'", len(retrieved), query[:60])
        return retrieved
