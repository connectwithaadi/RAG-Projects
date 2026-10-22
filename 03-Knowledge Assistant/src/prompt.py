"""
prompt.py
=========
Prompt construction for the RAG pipeline. Enforces context-grounded answers.
"""

from __future__ import annotations

from typing import Dict, List, Optional

FALLBACK_ANSWER = "I couldn't find that information in the uploaded documents."

SYSTEM_INSTRUCTIONS = f"""You are the Company Knowledge Assistant, an internal AI assistant that answers
questions strictly using the provided document context.

Rules you must always follow:
1. Answer ONLY using the information present in the "Context" section below.
2. Do not use outside knowledge, assumptions, or information not present in the context.
3. If the answer is not contained in the context, respond exactly with:
   "{FALLBACK_ANSWER}"
4. Be concise, accurate, and professional.
5. When useful, refer to the source document names provided in the context.
"""


def format_context(retrieved_chunks: List[Dict]) -> str:
    """Format retrieved chunks into a numbered context block with sources."""
    if not retrieved_chunks:
        return "No relevant context was found."

    lines = []
    for i, chunk in enumerate(retrieved_chunks, start=1):
        lines.append(
            f"[{i}] Source: {chunk['source']} (relevance: {chunk['score']})\n{chunk['text']}"
        )
    return "\n\n".join(lines)


def format_history(chat_history: List[Dict]) -> str:
    """Format prior turns of conversation for inclusion in the prompt."""
    if not chat_history:
        return "No previous conversation."

    lines = []
    for turn in chat_history:
        lines.append(f"User: {turn['question']}\nAssistant: {turn['answer']}")
    return "\n\n".join(lines)


def build_prompt(
    question: str,
    retrieved_chunks: List[Dict],
    chat_history: Optional[List[Dict]] = None,
) -> str:
    """Build the final prompt sent to Gemini."""
    context_block = format_context(retrieved_chunks)
    history_block = format_history(chat_history or [])

    return f"""{SYSTEM_INSTRUCTIONS}

Conversation history:
{history_block}

Context:
{context_block}

Question: {question}

Answer:"""
