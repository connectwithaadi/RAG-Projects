
import subprocess
import sys
from pathlib import Path

import streamlit as st
from core.rag_pipeline import RAGPipeline

ROOT = Path(__file__).resolve().parent

st.set_page_config(
    page_title="PDF Chatbot",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Enterprise PDF Chatbot")

st.markdown(
    "Ask questions about your uploaded PDFs using "
    "RAG powered by Groq GPT-OSS 120B."
)

if "rag" not in st.session_state:
    st.session_state.rag = RAGPipeline()

if "history" not in st.session_state:
    st.session_state.history = []

uploaded_file = st.sidebar.file_uploader(
    "Upload PDF",
    type=["pdf"],
    key="pdf_uploader"
)

if uploaded_file and st.sidebar.button("Process PDF"):
    raw_dir = ROOT / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    save_path = raw_dir / Path(uploaded_file.name).name

    with open(save_path, "wb") as f:
        f.write(uploaded_file.getvalue())

    scripts = [
        "ingest.py",
        "chunk_documents.py",
        "build_vector_store.py"
    ]

    try:
        for script in scripts:
            with st.spinner(f"Running {script}..."):
                result = subprocess.run(
                    [sys.executable, str(ROOT / script)],
                    cwd=str(ROOT),
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace"
                )

            if result.returncode != 0:
                st.error(f"{script} failed")
                st.code(result.stderr or result.stdout)
                st.stop()

        # Reload pipeline so it reads the newly built FAISS index.
        st.session_state.rag = RAGPipeline()
        st.session_state.history = []

        st.sidebar.success("PDF processed successfully!")
        st.rerun()

    except Exception as e:
        st.error(f"Processing failed: {e}")

question = st.chat_input("Ask a question...")

if question:
    with st.spinner("Searching your PDFs..."):
        response = st.session_state.rag.ask(question)

    st.session_state.history.append((question, response))

for user_question, response in st.session_state.history:
    with st.chat_message("user"):
        st.write(user_question)

    with st.chat_message("assistant"):
        st.write(response["answer"])

        with st.expander("Sources"):
            for source in response["sources"]:
                st.markdown(
                    f"**File:** {source['filename']}\n\n"
                    f"**Page:** {source['page']}\n\n"
                    f"**Similarity:** {source['score']:.3f}\n\n"
                    f"---\n\n{source['text']}"
                )
