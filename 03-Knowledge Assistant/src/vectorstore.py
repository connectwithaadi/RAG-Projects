"""
vectorstore.py
==============
FAISS-backed vector store with save/load/update/search support.
"""

from __future__ import annotations

import json
import logging
import os
import pickle
from dataclasses import dataclass
from typing import List, Optional, Tuple

import faiss
import numpy as np

logger = logging.getLogger(__name__)

INDEX_FILENAME = "index.faiss"
METADATA_FILENAME = "metadata.pkl"


class VectorStoreError(Exception):
    """Raised for vector store initialization, persistence, or search errors."""


@dataclass
class ChunkMetadata:
    """Metadata stored alongside each vector in the FAISS index."""

    text: str
    source: str
    chunk_id: int


class FAISSVectorStore:
    """
    Thin, persistent wrapper around a FAISS flat inner-product index.

    Embeddings are expected to already be L2-normalized (see
    `EmbeddingModel`), so inner product search is equivalent to cosine
    similarity search.
    """

    def __init__(self, dimension: Optional[int] = None) -> None:
        self.dimension = dimension
        self.index: Optional[faiss.Index] = None
        self.metadata: List[ChunkMetadata] = []

        if dimension is not None:
            self._init_index(dimension)

    def _init_index(self, dimension: int) -> None:
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        logger.info("Initialized FAISS IndexFlatIP with dimension=%d", dimension)

    def add(self, embeddings: np.ndarray, metadata_list: List[ChunkMetadata]) -> None:
        """Add new embeddings + metadata to the index (creates it if needed)."""
        if embeddings.shape[0] != len(metadata_list):
            raise VectorStoreError("Number of embeddings must match number of metadata entries.")

        if self.index is None:
            self._init_index(embeddings.shape[1])

        try:
            self.index.add(embeddings.astype("float32"))
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to add embeddings to FAISS index.")
            raise VectorStoreError(f"Failed to add vectors to index: {exc}") from exc

        self.metadata.extend(metadata_list)
        logger.info("Added %d vectors. Total vectors: %d", len(metadata_list), self.index.ntotal)

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[ChunkMetadata, float]]:
        """Return the top_k most similar (metadata, score) pairs."""
        if self.index is None or self.index.ntotal == 0:
            raise VectorStoreError("Vector store is empty or missing. Upload documents first.")

        query = np.asarray(query_embedding, dtype="float32").reshape(1, -1)
        top_k = min(top_k, self.index.ntotal)

        try:
            scores, indices = self.index.search(query, top_k)
        except Exception as exc:  # noqa: BLE001
            logger.exception("FAISS search failed.")
            raise VectorStoreError(f"Vector search failed: {exc}") from exc

        results: List[Tuple[ChunkMetadata, float]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            results.append((self.metadata[idx], float(score)))
        return results

    def save(self, directory: str) -> None:
        """Persist the FAISS index and metadata to disk."""
        if self.index is None:
            raise VectorStoreError("Cannot save an uninitialized vector store.")

        os.makedirs(directory, exist_ok=True)
        try:
            faiss.write_index(self.index, os.path.join(directory, INDEX_FILENAME))
            with open(os.path.join(directory, METADATA_FILENAME), "wb") as file_handle:
                pickle.dump(self.metadata, file_handle)
            with open(os.path.join(directory, "config.json"), "w", encoding="utf-8") as file_handle:
                json.dump({"dimension": self.dimension, "count": len(self.metadata)}, file_handle)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to save vector store.")
            raise VectorStoreError(f"Failed to save vector store to '{directory}': {exc}") from exc

        logger.info("Vector store saved to: %s", directory)

    def load(self, directory: str) -> None:
        """Load a previously persisted FAISS index and metadata from disk."""
        index_path = os.path.join(directory, INDEX_FILENAME)
        metadata_path = os.path.join(directory, METADATA_FILENAME)

        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            raise VectorStoreError(
                f"No vector store found at '{directory}'. Upload and process documents first."
            )

        try:
            self.index = faiss.read_index(index_path)
            with open(metadata_path, "rb") as file_handle:
                self.metadata = pickle.load(file_handle)
            self.dimension = self.index.d
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to load vector store.")
            raise VectorStoreError(f"Failed to load vector store from '{directory}': {exc}") from exc

        logger.info("Vector store loaded from: %s (%d vectors)", directory, self.index.ntotal)

    def exists(self, directory: str) -> bool:
        """Check whether a persisted vector store exists at `directory`."""
        return os.path.exists(os.path.join(directory, INDEX_FILENAME))

    @property
    def count(self) -> int:
        return 0 if self.index is None else self.index.ntotal
