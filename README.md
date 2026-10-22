# 🚀 RAG Projects — Retrieval-Augmented Generation

A collection of hands-on **Retrieval-Augmented Generation (RAG) projects** built to explore how Large Language Models (LLMs) can work with custom documents, retrieve relevant information, and generate context-aware answers.

This repository demonstrates the evolution of document-based AI applications, from querying a single PDF book to building an enterprise-style knowledge assistant with multiple document formats, conversation memory, a REST API, and Docker support.

The projects focus on practical AI engineering concepts, including document ingestion, text chunking, embeddings, vector databases, semantic search, retrieval strategies, prompt engineering, and grounded answer generation.

## 📂 Projects Overview

| # | Project | Description | Key Technologies |
|---|---|---|---|
| 01 | [RAG Book Assistant](./01-RAG_Book_Assistant) | Ask questions about PDF books using semantic retrieval and MMR. | LangChain, OpenAI, ChromaDB, Streamlit |
| 02 | [Enterprise PDF Chatbot](./02-PDF-Chatbot) | Upload PDFs and receive context-aware answers with source references. | Sentence Transformers, FAISS, Groq, Streamlit |
| 03 | [Company Knowledge Assistant](./03-Knowledge%20Assistant) | Query PDF, DOCX, and TXT documents through an enterprise-style RAG application. | Sentence Transformers, FAISS, Groq, FastAPI, Streamlit, Docker |

> Folder names and links should match the actual directory names in the repository.

---

## 01. 📚 RAG Book Assistant

A document-based RAG application that allows users to upload PDF books and ask questions about their content.

The application extracts document text, splits it into chunks, generates embeddings, and stores them in ChromaDB. When a user asks a question, an MMR retriever selects relevant chunks that are passed to an LLM to generate a context-grounded answer.

### ✨ Key Features

- Upload and process PDF books.
- Extract text using PyPDFLoader.
- Split documents using RecursiveCharacterTextSplitter.
- Generate embeddings using OpenAI Embeddings.
- Store and retrieve document vectors using ChromaDB.
- Retrieve relevant and diverse chunks using Maximum Marginal Relevance (MMR).
- Generate answers using OpenAI GPT.
- Restrict responses to retrieved document context.
- Provide an interactive Streamlit interface.
- Persist the local vector database.

### 🏗️ Architecture

```text
        PDF Book
            |
            v
       PyPDFLoader
            |
            v
    Recursive Text Splitter
     (1000 / 200 overlap)
            |
            v
     OpenAI Embeddings
            |
            v
         ChromaDB
            |
            |       User Query
            |            |
            |            v
            |       MMR Retriever
            |            |
            |            v
            |     Relevant Chunks
            |            |
            |            v
            |      Context + Query
            |            |
            |            v
            |          GPT LLM
            |            |
            |            v
            |       AI Answer
```

### 🛠️ Tech Stack

Python · LangChain · PyPDF · OpenAI Embeddings · ChromaDB · OpenAI GPT · Streamlit

---

## 02. 📄 Enterprise PDF Chatbot

An AI-powered PDF question-answering application built with RAG. Users can upload PDF documents, ask natural-language questions, and receive answers grounded in retrieved passages, along with source information.

The project uses Sentence Transformers to create semantic embeddings, FAISS for similarity search, and Groq for LLM-powered answer generation.

### ✨ Key Features

- Extract text from PDF documents.
- Process PDF content page by page.
- Split text into configurable, overlapping chunks.
- Generate embeddings using Sentence Transformers.
- Build a searchable FAISS vector index.
- Generate context-aware answers using Groq.
- Display source references, including filenames, page numbers, and similarity scores.
- Provide an interactive Streamlit chat interface.
- Manage API credentials through environment variables.
- Organize ingestion, chunking, indexing, and retrieval into separate modules and scripts.

### 🏗️ Architecture

```text
       PDF Documents
             |
             v
       PDF Extraction
             |
             v
        Text Chunking
             |
             v
    Sentence Transformers
          Embeddings
             |
             v
         FAISS Index
             |
             |       User Query
             |            |
             |            v
             |    Query Embedding
             |            |
             |            v
             |    Similarity Search
             |            |
             |            v
             |    Relevant Chunks
             |            |
             |            v
             |   Context + Question
             |            |
             |            v
             |        Groq LLM
             |            |
             |            v
             |     Answer + Sources
```

### 🛠️ Tech Stack

Python · Streamlit · LangChain Text Splitters · Sentence Transformers · FAISS · Groq · python-dotenv

---

## 03. 🏢 Company Knowledge Assistant

An enterprise-style document question-answering system that allows users to upload PDF, DOCX, and TXT files and ask questions about their content.

The application combines semantic retrieval with LLM-based answer generation. It also explores conversation memory for follow-up questions, persistent vector storage, a FastAPI backend, and Docker-based containerization.

### ✨ Key Features

- Support for PDF, DOCX, and TXT documents.
- Modular document loading and text splitting.
- Semantic embeddings using Sentence Transformers.
- Vector indexing and retrieval using FAISS.
- Context-aware answer generation through Groq.
- Source references for retrieved information.
- Conversation memory for follow-up questions.
- Persistent FAISS vector storage.
- Interactive Streamlit user interface.
- FastAPI backend for API-based access.
- Docker support for containerization.
- Environment-based application configuration.

### 🏗️ Architecture

**Document ingestion pipeline**

```text
 PDF / DOCX / TXT
         |
         v
   Document Loader
         |
         v
     Text Splitter
         |
         v
 Sentence Transformers
      Embeddings
         |
         v
    FAISS Vector Store
```

**Question-answering pipeline**

```text
       User Question
             |
             v
       Query Processing
             |
             v
      FAISS Retriever
             |
             v
      Relevant Chunks
             |
             v
     Prompt Construction
   (Question + Context
    + Chat History)
             |
             v
          Groq LLM
             |
             v
      Generated Answer
             |
             v
       Source References
```

**Application interfaces:** Streamlit UI and FastAPI backend.

### 🛠️ Tech Stack

Python · Streamlit · FastAPI · Sentence Transformers · FAISS · Groq · Docker · python-dotenv

---

## 🧠 Core RAG Concepts Demonstrated

| Concept | What It Demonstrates |
|---|---|
| Document Loading | Extracting text from different document formats |
| Text Chunking | Splitting large documents into smaller, retrievable sections |
| Chunk Overlap | Preserving context between neighboring chunks |
| Embeddings | Representing text as numerical vectors |
| Vector Databases / Indexes | Storing vectors for efficient retrieval |
| Semantic Search | Finding content related to the meaning of a query |
| MMR Retrieval | Balancing relevance and diversity in retrieved chunks |
| Prompt Engineering | Combining retrieved context and questions for generation |
| Grounded Generation | Using retrieved document content to guide LLM answers |
| Source References | Connecting generated answers with retrieved documents |
| Conversation Memory | Supporting follow-up questions using chat history |
| REST API | Exposing application functionality through FastAPI |
| Containerization | Packaging an application with Docker |

## 🔄 Overall RAG Workflow

The projects follow the core RAG lifecycle:

```text
       Documents
           |
           v
     Text Extraction
           |
           v
       Chunking
           |
           v
      Embeddings
           |
           v
    Vector Storage
           |
           v
       User Query
           |
           v
       Retrieval
           |
           v
   Relevant Context
           |
           v
   Prompt Construction
           |
           v
      LLM Generation
           |
           v
   Context-Aware Answer
```

The individual projects extend this workflow with different vector stores, retrieval strategies, interfaces, source references, conversation memory, and application deployment components.

## 🎯 Learning Objectives

Through these projects, the goal is to:

- Understand the complete RAG pipeline from document ingestion to answer generation.
- Build document-aware question-answering applications.
- Work with embedding models and vector search.
- Compare ChromaDB and FAISS-based retrieval workflows.
- Explore MMR and semantic similarity retrieval.
- Build interfaces for interacting with LLM applications.
- Improve answer traceability through source references.
- Understand the role of prompt construction and conversation memory.
- Separate application logic into reusable modules.
- Explore API development and Docker-based deployment.

## 🔐 Security and Reliability

- Store API keys in environment variables or platform-managed secrets.
- Never commit `.env` files or API credentials to GitHub.
- Treat retrieved passages as supporting context, not a guarantee of correctness.
- Verify important answers against their original documents.
- Consider OCR for scanned PDFs and validate extracted text quality.
- Test retrieval quality, source attribution, and error handling before deployment.

## 🚀 Future Improvements

- Add hybrid retrieval combining keyword search and semantic search.
- Introduce a reranking model for improved retrieval relevance.
- Add automated RAG evaluation using metrics such as Recall@K, Precision@K, and MRR.
- Improve page-level citations and source previews.
- Support larger document collections and metadata filtering.
- Add streaming responses and authentication.
- Build automated tests and CI/CD workflows.
- Deploy applications using cloud infrastructure and container orchestration.
- Compare retrieval quality, latency, and token costs across implementations.

## 👨‍💻 Author

**Aditya Kumar Singh (Aadi)**

GitHub: [@connectwithaadi](https://github.com/connectwithaadi)

Repository: [RAG-Projects](https://github.com/connectwithaadi/RAG-Projects)

---

*Built as part of a hands-on journey toward Generative AI and AI Engineering, with a focus on retrieval systems, LLM applications, and practical RAG architectures.*
