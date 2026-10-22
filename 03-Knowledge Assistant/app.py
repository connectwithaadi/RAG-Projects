"""
app.py
======
Command-line entry point for the Company Knowledge Assistant.

Usage:
    python app.py --docs data/uploaded_docs/file1.pdf data/uploaded_docs/file2.docx

If no --docs are given, the app will try to load an existing vector store
from data/vector_store/, or ingest any files already sitting in
data/uploaded_docs/.
"""

from __future__ import annotations

import argparse
import glob
import os
import sys

from src.rag_chain import RAGChain
from src.utils import setup_logging, settings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Company Knowledge Assistant CLI")
    parser.add_argument(
        "--docs",
        nargs="*",
        default=None,
        help="Paths to documents to ingest before chatting.",
    )
    return parser.parse_args()


def main() -> None:
    setup_logging()
    args = parse_args()

    rag_chain = RAGChain()

    docs = args.docs
    if not docs:
        docs = glob.glob(os.path.join(settings.upload_dir, "*"))

    if docs:
        print(f"Ingesting {len(docs)} document(s)...")
        try:
            chunks = rag_chain.ingest(docs)
            rag_chain.save_index()
            print(f"Indexed {chunks} chunks.")
        except Exception as exc:  # noqa: BLE001
            print(f"Failed to ingest documents: {exc}")
    elif rag_chain.vector_store.exists(settings.vector_store_dir):
        rag_chain.load_index()
        print("Loaded existing vector store.")
    else:
        print("No documents found. Add files to data/uploaded_docs/ or pass --docs.")
        sys.exit(1)

    print("\nCompany Knowledge Assistant is ready. Type 'exit' to quit.\n")
    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if question.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if not question:
            continue

        result = rag_chain.ask(question)
        print(f"Assistant: {result['answer']}")
        if result["sources"]:
            print(f"Sources: {', '.join(result['sources'])}")
        print()


if __name__ == "__main__":
    main()
