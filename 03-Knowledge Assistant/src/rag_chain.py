
"""
rag_chain.py
============
End-to-end Retrieval Augmented Generation pipeline:

Documents -> Chunking -> Embeddings -> Vector Store -> Retriever
-> Prompt -> Groq -> Answer
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from .chat_memory import ConversationMemory
from .embeddings import EmbeddingModel
from .loader import DocumentLoader
from .prompt import FALLBACK_ANSWER, build_prompt
from .retriever import Retriever
from .splitter import TextSplitter
from .utils import GroqClient, GroqError, settings
from .vectorstore import ChunkMetadata, FAISSVectorStore, VectorStoreError

logger = logging.getLogger(__name__)


class RAGChain:
    """Orchestrates document ingestion and RAG question answering using Groq."""

    def __init__(
        self,
        groq_api_key: Optional[str] = None,
        chunk_size: int = settings.chunk_size,
        chunk_overlap: int = settings.chunk_overlap,
        top_k: int = settings.top_k,
        memory_limit: int = settings.memory_limit,
    ) -> None:
        self.loader = DocumentLoader()
        self.splitter = TextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        self.embedding_model = EmbeddingModel()
        self.vector_store = FAISSVectorStore()
        self.retriever = Retriever(
            self.vector_store,
            self.embedding_model,
            top_k=top_k,
        )
        self.memory = ConversationMemory(max_length=memory_limit)
        self.groq_client = GroqClient(api_key=groq_api_key)

    def ingest(self, filepaths: List[str]) -> int:
        """Load, chunk, embed, and index documents."""

        if not filepaths:
            raise ValueError("No files provided for ingestion.")

        documents = self.loader.load_multiple(filepaths)
        if not documents:
            raise ValueError("None of the provided files could be loaded.")

        chunks = self.splitter.split_documents(documents)
        if not chunks:
            raise ValueError(
                "Document splitting produced no chunks "
                "(documents may be empty)."
            )

        texts = [chunk.text for chunk in chunks]
        embeddings = self.embedding_model.embed_documents(texts)

        metadata_list = [
            ChunkMetadata(
                text=chunk.text,
                source=chunk.source,
                chunk_id=chunk.chunk_id,
            )
            for chunk in chunks
        ]

        self.vector_store.add(embeddings, metadata_list)

        logger.info(
            "Ingested %d documents into %d chunks.",
            len(documents),
            len(chunks),
        )
        return len(chunks)

    def save_index(
        self,
        directory: str = settings.vector_store_dir,
    ) -> None:
        """Save the FAISS vector store."""
        self.vector_store.save(directory)

    def load_index(
        self,
        directory: str = settings.vector_store_dir,
    ) -> None:
        """Load a previously saved FAISS vector store."""
        self.vector_store.load(directory)

    def ask(self, question: str) -> Dict:
        """Answer a question using retrieved context and Groq."""

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        try:
            retrieved_chunks = self.retriever.retrieve(question)
        except VectorStoreError as exc:
            logger.warning("Retrieval unavailable: %s", exc)
            retrieved_chunks = []

        if not retrieved_chunks:
            answer = FALLBACK_ANSWER
            sources: List[str] = []
        else:
            prompt = build_prompt(
                question,
                retrieved_chunks,
                self.memory.get_history(),
            )

            try:
                answer = self.groq_client.generate(prompt)
            except GroqError as exc:
                logger.error("Groq generation failed: %s", exc)
                answer = (
                    "An error occurred while generating the answer: "
                    f"{exc}"
                )

            sources = sorted(
                {chunk["source"] for chunk in retrieved_chunks}
            )

        self.memory.add_exchange(question, answer)

        return {
            "answer": answer,
            "sources": sources,
            "retrieved_chunks": retrieved_chunks,
        }

    def reset(self) -> None:
        """Clear conversation memory without deleting the vector store."""
        self.memory.clear()
