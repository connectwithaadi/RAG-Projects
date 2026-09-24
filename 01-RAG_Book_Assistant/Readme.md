`# 📚 RAG Book Assistant

A document-based **Retrieval-Augmented Generation (RAG)** application that allows users to upload PDF books and ask questions about their content.

The application retrieves relevant information from the uploaded document using semantic search and provides answers using an LLM while restricting the model to the retrieved document context.

---

### 🖥️ Application Preview

![Credit Risk Assessment App](screenshots/rag.png)
---


## 🚀 Features

- 📄 Upload PDF books
- 🔍 Extract text from PDF documents
- ✂️ Split documents into manageable chunks
- 🧠 Generate embeddings using OpenAI Embeddings
- 🗄️ Store document embeddings in ChromaDB
- 🎯 Retrieve relevant chunks using MMR
- 🤖 Generate answers using OpenAI GPT
- 🛡️ Context-restricted responses to reduce hallucinations
- 🖥️ Interactive Streamlit interface
- 💾 Persistent local vector database

---

## 🏗️ RAG Architecture

```text
                 ┌─────────────────┐
                 │    PDF Book     │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  PyPDFLoader    │
                 └────────┬────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ Recursive Text Splitter│
              │ chunk_size = 1000     │
              │ overlap = 200         │
              └───────────┬───────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ OpenAI Embedding│
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │    ChromaDB     │
                 └────────┬────────┘
                          │
                     User Query
                          │
                          ▼
                 ┌─────────────────┐
                 │  MMR Retriever  │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Relevant Context│
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │      GPT LLM    │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │   AI Answer     │
                 └─────────────────┘
```

---

## 🧠 How RAG Works in This Project

The application follows four major stages:

### 1. Document Loading
Uploaded PDF documents are loaded using `PyPDFLoader`:

```python
loader = PyPDFLoader(file_path)
docs = loader.load()
```

### 2. Document Chunking
Large documents are divided into smaller chunks using `RecursiveCharacterTextSplitter`:

```python
RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
```

The overlap helps preserve contextual information between neighboring chunks.

### 3. Embeddings & Vector Database
Each chunk is converted into an embedding using OpenAI Embeddings and stored in ChromaDB:

```text
Document Chunk
      ↓
Embedding Model
      ↓
Vector Representation
      ↓
ChromaDB
```

### 4. Retrieval & Generation
When the user asks a question:

```text
Question
   ↓
MMR Retriever
   ↓
Relevant Document Chunks
   ↓
Context
   ↓
GPT
   ↓
Answer
```

The application instructs the LLM to use only the retrieved context. If the required information is not available, the system responds:

> *I could not find the answer in the document.*

---

## 🎯 Retrieval Strategy

This project uses Maximum Marginal Relevance (MMR) retrieval:

```python
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 4,
        "fetch_k": 10,
        "lambda_mult": 0.5
    }
)
```

### Retrieval Configuration

| Parameter | Value | Purpose |
| :--- | :--- | :--- |
| `k` | `4` | Final relevant chunks returned |
| `fetch_k` | `10` | Candidate chunks considered |
| `lambda_mult` | `0.5` | Balance relevance and diversity |

MMR helps retrieve relevant information while avoiding overly similar chunks.

---

## 🛠️ Tech Stack

| Technology | Purpose |
| :--- | :--- |
| **Python** | Core programming language |
| **LangChain** | RAG orchestration |
| **PyPDF** | PDF processing |
| **OpenAI Embeddings** | Text embeddings |
| **ChromaDB** | Vector database |
| **OpenAI GPT** | Answer generation |
| **Streamlit** | Web application UI |
| **python-dotenv** | Environment variable management |

The project dependencies include LangChain, LangChain OpenAI integrations, ChromaDB, PDF/document processing libraries, Streamlit, and environment-variable tooling.

---

## 📂 Project Structure

```text
RAG_Book_Assistant/
│
├── 📁 Screenshots/
│   └── rag.png
│
├── 📁 document_loaders/
│   └── deeplearning.pdf
│
├── 📁 chroma_db/
│   └── Vector database files
│
├── 📄 app.py
├── 📄 create_database.py
├── 📄 main.py
├── 📄 requirements.txt
└── 📄 README.md
```

### File Breakdown

- **`app.py`**: Main Streamlit application. Handles PDF upload, document processing, vector database creation, retrieval, and question answering. The complete interactive application flow is implemented here.
- **`create_database.py`**: Responsible for creating the vector database (`PDF` $\rightarrow$ `PyPDFLoader` $\rightarrow$ `Chunking` $\rightarrow$ `Embeddings` $\rightarrow$ `ChromaDB`).
- **`main.py`**: Contains the core retrieval and generation pipeline. It loads ChromaDB, creates the MMR retriever, retrieves relevant documents, and sends the resulting context to the LLM.

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd RAG_Book_Assistant
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

- **Windows:**
  ```bash
  venv\Scripts\activate
  ```
- **Linux / macOS:**
  ```bash
  source venv/bin/activate
  ```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key
```

---

## ▶️ Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

Then open the local Streamlit URL displayed in the terminal.

---

## 💡 Example

1. Upload a book such as `deeplearning.pdf`.
2. Ask a question:
   ```text
   Explain Recurrent Neural Networks.
   ```
3. The system retrieves relevant sections from the book and generates a grounded response.

---

## 🔐 Context-Grounded Generation

The system prompt explicitly instructs the model:

> *"Use ONLY the provided context to answer the question."*

If the answer cannot be found in the retrieved document context, the application returns:

> *"I could not find the answer in the document."*

This creates a grounded generation pattern instead of allowing the model to hallucinate or answer freely from its pre-training data.

---

## 📸 Application Workflow

```text
User
 │
 ▼
Upload PDF
 │
 ▼
PyPDFLoader
 │
 ▼
Text Splitting
 │
 ▼
OpenAI Embeddings
 │
 ▼
ChromaDB
 │
 ▼
User Question
 │
 ▼
MMR Retrieval
 │
 ▼
Relevant Context
 │
 ▼
Prompt Template
 │
 ▼
GPT
 │
 ▼
AI Answer
```

---

## 📚 Concepts Demonstrated

- Retrieval-Augmented Generation (RAG)
- Document loaders & PyPDF
- Text chunking & chunk overlap
- Vector embeddings
- Vector databases (ChromaDB)
- Semantic search & Maximum Marginal Relevance (MMR)
- Prompt templates & Context injection
- LLM integration & Grounded generation
- Streamlit application development
- Persistent local vector storage

---

## 🚀 Future Improvements

- [ ] Support multiple PDFs simultaneously
- [ ] Add source/page citations to answers
- [ ] Add document metadata filtering
- [ ] Add hybrid search (BM25 + Semantic)
- [ ] Add reranking (e.g., Cohere rerank)
- [ ] Add conversation memory / chat history
- [ ] Add streaming responses
- [ ] Add RAG evaluation metrics (Ragas / TruLens)
- [ ] Build a separate FastAPI backend
- [ ] Cloud deployment & containerization (Docker)
- [ ] User authentication
- [ ] Support additional file formats (`.docx`, `.txt`, `.epub`)

---

## 🎯 Learning Goal

This project was built to understand the complete lifecycle of a practical RAG application:

```text
Documents ──▶ Chunking ──▶ Embeddings ──▶ Vector DB ──▶ Retrieval ──▶ Context ──▶ LLM ──▶ Grounded Answer
```

It serves as an AI Engineering project demonstrating how LLMs can be securely connected to private and custom document data.

---

## 👨‍💻 Author

**Aditya Kumar Singh**  
