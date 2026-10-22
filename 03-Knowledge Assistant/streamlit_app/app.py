

"""
streamlit_app/app.py
=====================
Streamlit UI for the Company Knowledge Assistant.
Powered by Groq and Retrieval Augmented Generation (RAG).
"""

from __future__ import annotations

import os
import sys

import streamlit as st

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from src.rag_chain import RAGChain  # noqa: E402
from src.utils import setup_logging, settings  # noqa: E402

setup_logging()

st.set_page_config(
    page_title="Company Knowledge Assistant",
    page_icon="📚",
    layout="wide",
)


@st.cache_resource(show_spinner=False)
def get_rag_chain(api_key: str) -> RAGChain:
    """Create and cache the RAG chain using the Groq API key."""
    return RAGChain(groq_api_key=api_key)


def init_session_state() -> None:
    """Initialize Streamlit session state."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "documents_indexed" not in st.session_state:
        st.session_state.documents_indexed = 0


def render_sidebar():
    """Render API configuration and document management controls."""

    st.sidebar.title("📚 Company Knowledge Assistant")
    st.sidebar.markdown(
        "Enterprise RAG powered by **Groq**."
    )

    api_key = st.sidebar.text_input(
        "Groq API Key",
        value=os.getenv("GROQ_API_KEY", settings.groq_api_key),
        type="password",
        help=(
            "Enter your Groq API key. "
            "Get one at https://console.groq.com/keys"
        ),
    )

    if not api_key or api_key == "PASTE_YOUR_API_KEY_HERE":
        st.sidebar.warning(
            "Enter your Groq API key to get started."
        )
        return None

    rag_chain = get_rag_chain(api_key)

    st.sidebar.divider()
    st.sidebar.subheader("Upload documents")

    uploaded_files = st.sidebar.file_uploader(
        "PDF, DOCX, or TXT",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )

    if uploaded_files and st.sidebar.button(
        "Process documents",
        use_container_width=True,
    ):
        os.makedirs(settings.upload_dir, exist_ok=True)
        saved_paths = []

        for uploaded_file in uploaded_files:
            destination = os.path.join(
                settings.upload_dir,
                uploaded_file.name,
            )

            with open(destination, "wb") as file_handle:
                file_handle.write(uploaded_file.getbuffer())

            saved_paths.append(destination)

        with st.spinner("Indexing documents..."):
            try:
                chunks_indexed = rag_chain.ingest(saved_paths)
                rag_chain.save_index()

                st.session_state.documents_indexed += chunks_indexed

                st.sidebar.success(
                    f"Indexed {chunks_indexed} chunks "
                    f"from {len(saved_paths)} file(s)."
                )

            except Exception as exc:  # noqa: BLE001
                st.sidebar.error(
                    f"Failed to process documents: {exc}"
                )

    st.sidebar.divider()
    st.sidebar.metric(
        "Chunks indexed",
        st.session_state.documents_indexed,
    )

    if st.sidebar.button(
        "Reset conversation",
        use_container_width=True,
    ):
        rag_chain.reset()
        st.session_state.messages = []
        st.sidebar.success("Conversation reset.")

    return rag_chain


def render_chat(rag_chain) -> None:
    """Render the document question-answering interface."""

    st.title("💬 Ask your documents")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message.get("sources"):
                with st.expander("Sources"):
                    for source in message["sources"]:
                        st.markdown(f"- {source}")

    question = st.chat_input(
        "Ask a question about your uploaded documents..."
    )

    if question:
        st.session_state.messages.append(
            {"role": "user", "content": question}
        )

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    result = rag_chain.ask(question)
                    answer = result["answer"]
                    sources = result["sources"]

                except Exception as exc:  # noqa: BLE001
                    answer = f"An error occurred: {exc}"
                    sources = []

                st.markdown(answer)

                if sources:
                    with st.expander("Sources"):
                        for source in sources:
                            st.markdown(f"- {source}")

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "sources": sources,
            }
        )


def main() -> None:
    """Run the Streamlit application."""

    init_session_state()
    rag_chain = render_sidebar()

    if rag_chain is None:
        st.info(
            "👋 Enter your Groq API key in the sidebar to begin."
        )
        return

    render_chat(rag_chain)


if __name__ == "__main__":
    main()
