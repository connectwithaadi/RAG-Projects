"""
chat_memory.py
==============
Simple bounded conversation memory for the RAG chatbot.
"""

from __future__ import annotations

import logging
from collections import deque
from typing import Deque, Dict, List

logger = logging.getLogger(__name__)


class ConversationMemory:
    """Stores the most recent question/answer pairs, up to a fixed limit."""

    def __init__(self, max_length: int = 10) -> None:
        if max_length <= 0:
            raise ValueError("max_length must be a positive integer.")
        self.max_length = max_length
        self._history: Deque[Dict[str, str]] = deque(maxlen=max_length)

    def add_exchange(self, question: str, answer: str) -> None:
        """Add a question/answer pair, evicting the oldest if over the limit."""
        self._history.append({"question": question, "answer": answer})
        logger.debug("Memory size: %d/%d", len(self._history), self.max_length)

    def get_history(self) -> List[Dict[str, str]]:
        return list(self._history)

    def clear(self) -> None:
        self._history.clear()
        logger.info("Conversation memory cleared.")

    def __len__(self) -> int:
        return len(self._history)
