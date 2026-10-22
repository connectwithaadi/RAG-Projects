
"""
splitter.py
===========
Custom, configurable text chunking utilities.

Implements a sentence-aware character-based splitter so that chunk
boundaries prefer to fall on sentence edges rather than mid-word, while
still respecting a hard chunk_size limit and a configurable overlap.
This is a custom implementation and does not rely solely on LangChain's
default splitters.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import List

logger = logging.getLogger(__name__)

_SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?])\s+")


@dataclass
class Chunk:
    """A single chunk of text with metadata about its source document."""

    text: str
    chunk_id: int
    source: str
    start_char: int
    end_char: int


class TextSplitter:
    """
    Custom sentence-aware text splitter.

    Sentences are packed greedily into chunks up to `chunk_size`
    characters. When a chunk is full, `chunk_overlap` trailing characters
    from the previous chunk are carried into the next one for context
    continuity.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 150) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be a positive integer.")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative.")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size.")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _split_sentences(self, text: str) -> List[str]:
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            return []
        sentences = _SENTENCE_BOUNDARY_RE.split(text)
        return [s.strip() for s in sentences if s.strip()]

    def split_text(self, text: str) -> List[str]:
        """Split raw text into a list of chunk strings."""
        if not text or not text.strip():
            logger.warning("Attempted to split empty text.")
            return []

        sentences = self._split_sentences(text)
        chunks: List[str] = []
        current = ""

        for sentence in sentences:
            # Hard-split any single sentence longer than chunk_size.
            if len(sentence) > self.chunk_size:
                if current:
                    chunks.append(current.strip())
                    current = ""
                step = max(self.chunk_size - self.chunk_overlap, 1)
                for i in range(0, len(sentence), step):
                    piece = sentence[i:i + self.chunk_size]
                    chunks.append(piece.strip())
                continue

            candidate = f"{current} {sentence}".strip() if current else sentence

            if len(candidate) <= self.chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current.strip())
                overlap_text = current[-self.chunk_overlap:] if self.chunk_overlap else ""
                current = f"{overlap_text} {sentence}".strip()

        if current:
            chunks.append(current.strip())

        return [c for c in chunks if c]

    def split_documents(self, documents: List) -> List[Chunk]:
        """
        Split a list of loaded-document objects (must expose `.content`
        and `.filename`) into a flat list of Chunk objects.
        """
        all_chunks: List[Chunk] = []
        for doc in documents:
            text_chunks = self.split_text(doc.content)
            cursor = 0
            for idx, chunk_text in enumerate(text_chunks):
                start = doc.content.find(chunk_text[:50], cursor) if chunk_text else -1
                start = max(start, 0)
                end = start + len(chunk_text)
                cursor = end
                all_chunks.append(
                    Chunk(
                        text=chunk_text,
                        chunk_id=idx,
                        source=doc.filename,
                        start_char=start,
                        end_char=end,
                    )
                )
            logger.info("Split '%s' into %d chunks.", doc.filename, len(text_chunks))
        return all_chunks
