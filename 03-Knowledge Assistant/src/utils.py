"""
utils.py
========
Shared utilities: logging configuration, environment configuration,
and the Groq API client wrapper.
"""

from __future__ import annotations

import logging
import os
import sys
import time
from dataclasses import dataclass
from typing import Optional

from groq import Groq


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logging once for the whole application."""
    root_logger = logging.getLogger()

    if root_logger.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    root_logger.setLevel(level)


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class Settings:
    """Application configuration from environment variables."""

    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv(
        "GROQ_MODEL", "openai/gpt-oss-120b"
    )

    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "150"))
    top_k: int = int(os.getenv("TOP_K", "5"))
    score_threshold: float = float(
        os.getenv("SCORE_THRESHOLD", "0.0")
    )
    memory_limit: int = int(os.getenv("MEMORY_LIMIT", "10"))
    vector_store_dir: str = os.getenv(
        "VECTOR_STORE_DIR", "data/vector_store"
    )
    upload_dir: str = os.getenv(
        "UPLOAD_DIR", "data/uploaded_docs"
    )


settings = Settings()


# ---------------------------------------------------------------------------
# Groq client
# ---------------------------------------------------------------------------

class GroqError(Exception):
    """Raised when the Groq API fails or returns an error."""


class GroqClient:
    """
    Wrapper around the Groq SDK with retries, logging,
    and clear error messages for the RAG pipeline.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        max_retries: int = 2,
    ) -> None:
        self.api_key = api_key or settings.groq_api_key
        self.model_name = model_name or settings.groq_model
        self.max_retries = max_retries
        self._client: Optional[Groq] = None

        if (
            not self.api_key
            or self.api_key == "PASTE_YOUR_API_KEY_HERE"
        ):
            logger.warning(
                "GROQ_API_KEY is not set. "
                "Set it before making generation calls."
            )

    def _get_client(self) -> Groq:
        """Initialize the Groq client lazily."""
        if self._client is None:
            if (
                not self.api_key
                or self.api_key == "PASTE_YOUR_API_KEY_HERE"
            ):
                raise GroqError(
                    "GROQ_API_KEY is missing or still a placeholder. "
                    "Set your real Groq API key before chatting."
                )

            try:
                self._client = Groq(api_key=self.api_key)
            except Exception as exc:
                logger.exception("Failed to initialize Groq client.")
                raise GroqError(
                    f"Failed to initialize Groq client: {exc}"
                ) from exc

        return self._client

    def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
    ) -> str:
        """Generate a response from Groq, with retries."""

        client = self._get_client()
        last_exception: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 2):
            try:
                response = client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    temperature=temperature,
                )

                content = response.choices[0].message.content

                if not content or not content.strip():
                    raise GroqError(
                        "Groq returned an empty response."
                    )

                return content.strip()

            except Exception as exc:
                last_exception = exc

                logger.warning(
                    "Groq call failed (attempt %d/%d): %s",
                    attempt,
                    self.max_retries + 1,
                    exc,
                )

                if attempt <= self.max_retries:
                    time.sleep(min(2 ** attempt, 8))

        logger.error("Groq call failed after retries.")

        raise GroqError(
            f"Groq API call failed after "
            f"{self.max_retries + 1} attempts: {last_exception}"
        ) from last_exception
