"""
embeddings.py
=============
Embedding generation using Sentence-Transformers.
"""

from __future__ import annotations

import logging
from typing import List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class EmbeddingError(Exception):
    """Raised when embedding generation fails."""


class EmbeddingModel:
    """
    Reusable wrapper around a Sentence-Transformers embedding model.

    The underlying model is loaded lazily on first use to keep notebook
    startup fast, and is cached on the instance afterwards.
    """

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME) -> None:
        self.model_name = model_name
        self._model: Optional[SentenceTransformer] = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            logger.info("Loading embedding model: %s", self.model_name)
            try:
                self._model = SentenceTransformer(self.model_name)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Failed to load embedding model.")
                raise EmbeddingError(
                    f"Could not load embedding model '{self.model_name}': {exc}"
                ) from exc
        return self._model

    def embed_documents(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Embed a list of texts and return a float32 numpy array."""
        if not texts:
            raise EmbeddingError("Cannot embed an empty list of texts.")
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to embed documents.")
            raise EmbeddingError(f"Embedding generation failed: {exc}") from exc
        return embeddings.astype("float32")

    def embed_query(self, text: str) -> np.ndarray:
        """Embed a single query string."""
        if not text or not text.strip():
            raise EmbeddingError("Cannot embed an empty query string.")
        return self.embed_documents([text])[0]

    @property
    def dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()
