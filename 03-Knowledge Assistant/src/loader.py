"""
loader.py
=========
Document loading utilities for the Company Knowledge Assistant.

Supports loading and extracting raw text from PDF, DOCX, and TXT files.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import List, Optional

from pypdf import PdfReader
from docx import Document as DocxDocument

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


class DocumentLoadError(Exception):
    """Raised when a document cannot be loaded or parsed."""


class UnsupportedFileTypeError(DocumentLoadError):
    """Raised when a file extension is not supported by the loader."""


@dataclass
class LoadedDocument:
    """Container for a loaded document's raw content and metadata."""

    filename: str
    filepath: str
    content: str
    file_type: str


class DocumentLoader:
    """
    Reusable loader for extracting text from PDF, DOCX, and TXT files.

    Example:
        loader = DocumentLoader()
        doc = loader.load("data/uploaded_docs/policy.pdf")
        docs = loader.load_multiple(["a.pdf", "b.docx", "c.txt"])
    """

    def __init__(self) -> None:
        logger.debug("DocumentLoader initialized.")

    def load(self, filepath: str) -> LoadedDocument:
        """Load a single document and return its extracted text + metadata."""
        if not os.path.exists(filepath):
            logger.error("File not found: %s", filepath)
            raise FileNotFoundError(f"File not found: {filepath}")

        if os.path.getsize(filepath) == 0:
            logger.error("File is empty: %s", filepath)
            raise DocumentLoadError(f"File is empty: {filepath}")

        ext = os.path.splitext(filepath)[1].lower()

        try:
            if ext == ".pdf":
                content = self._load_pdf(filepath)
            elif ext == ".docx":
                content = self._load_docx(filepath)
            elif ext == ".txt":
                content = self._load_txt(filepath)
            else:
                raise UnsupportedFileTypeError(
                    f"Unsupported file type '{ext}'. Supported types: {SUPPORTED_EXTENSIONS}"
                )
        except UnsupportedFileTypeError:
            raise
        except DocumentLoadError:
            raise
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to load document: %s", filepath)
            raise DocumentLoadError(f"Failed to load '{filepath}': {exc}") from exc

        if not content or not content.strip():
            logger.warning("No extractable text found in: %s", filepath)

        return LoadedDocument(
            filename=os.path.basename(filepath),
            filepath=filepath,
            content=content.strip(),
            file_type=ext.replace(".", ""),
        )

    def load_multiple(self, filepaths: List[str]) -> List[LoadedDocument]:
        """Load several documents, skipping (and logging) any that fail."""
        documents: List[LoadedDocument] = []
        for filepath in filepaths:
            try:
                documents.append(self.load(filepath))
            except DocumentLoadError as exc:
                logger.error("Skipping file due to error: %s (%s)", filepath, exc)
                continue
        return documents

    @staticmethod
    def _load_pdf(filepath: str) -> str:
        try:
            reader = PdfReader(filepath)
        except Exception as exc:  # noqa: BLE001
            raise DocumentLoadError(f"Invalid or corrupted PDF file: {filepath}") from exc

        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception as exc:  # noqa: BLE001
                raise DocumentLoadError(f"Encrypted PDF could not be opened: {filepath}") from exc

        pages_text = []
        for page_number, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text() or ""
            except Exception:  # noqa: BLE001
                logger.warning("Failed to extract text from page %s of %s", page_number, filepath)
                text = ""
            pages_text.append(text)

        return "\n".join(pages_text)

    @staticmethod
    def _load_docx(filepath: str) -> str:
        try:
            doc = DocxDocument(filepath)
        except Exception as exc:  # noqa: BLE001
            raise DocumentLoadError(f"Invalid or corrupted DOCX file: {filepath}") from exc

        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]

        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells)
                if row_text.strip(" |"):
                    paragraphs.append(row_text)

        return "\n".join(paragraphs)

    @staticmethod
    def _load_txt(filepath: str) -> str:
        encodings = ["utf-8", "latin-1"]
        last_error: Optional[Exception] = None
        for encoding in encodings:
            try:
                with open(filepath, "r", encoding=encoding) as file_handle:
                    return file_handle.read()
            except UnicodeDecodeError as exc:
                last_error = exc
                continue
        raise DocumentLoadError(f"Could not decode text file '{filepath}': {last_error}")
