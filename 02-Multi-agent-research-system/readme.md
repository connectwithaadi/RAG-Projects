# 🔎 ResearchMind — Multi-Agent AI Research System

A **multi-agent AI research pipeline** built with **LangChain, OpenAI, Tavily, BeautifulSoup, Requests, and Streamlit**.

ResearchMind takes a research topic and processes it through a structured workflow:

**Search → Read → Write → Critique**

The project demonstrates how multiple AI agents and LLM chains can work together with external tools to produce a structured research report.

---


### 🖥️ Application Preview

![Multi AI Agent (Screenshots/multi.png)
---


## 🚀 Project Overview

ResearchMind is designed around the idea of giving different responsibilities to different AI components instead of asking a single LLM to perform the entire research task.

The pipeline contains:

1. **Search Agent** — searches the web using Tavily.
2. **Reader Agent** — selects a relevant URL and extracts deeper page content.
3. **Writer Chain** — combines the gathered information into a structured research report.
4. **Critic Chain** — reviews the generated report and provides a score, strengths, and improvement areas.

> Note: the project contains **2 agents + 2 LLM chains**, rather than four independent agents.

---

## 🧠 Architecture

```text
                    ┌─────────────────────┐
                    │   Research Topic    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Search Agent     │
                    │   LangChain Agent   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Tavily Search    │
                    │   Live Web Results  │
                    └──────────┬──────────┘
                               │
                         Search Results
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Reader Agent     │
                    │   LangChain Agent   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  scrape_url Tool    │
                    │ Requests + BS4      │
                    └──────────┬──────────┘
                               │
                         Scraped Content
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
          ┌─────────────────┐   ┌─────────────────┐
          │  Writer Chain   │   │  Critic Chain   │
          │ Research Report │   │ Review + Score  │
          └────────┬────────┘   └────────┬────────┘
                   │                     │
                   └──────────┬──────────┘
                              ▼
                    ┌─────────────────────┐
                    │     Final Output    │
                    └─────────────────────┘
```

---

## 📂 Project Structure

```text
ResearchMind/
│
├── agents.py              # Search & Reader agents + Writer/Critic chains
├── tools.py               # Tavily search and URL scraping tools
├── pipeline.py            # Orchestrates the complete research workflow
├── app.py                 # Streamlit user interface
├── requirements.txt       # Python dependencies
├── .env                   # API keys (not committed)
└── README.md
```

### File Responsibilities

| File | Responsibility |
|---|---|
| `agents.py` | Creates the Search Agent, Reader Agent, Writer Chain and Critic Chain |
| `tools.py` | Defines custom LangChain tools for web search and web scraping |
| `pipeline.py` | Runs all stages in the correct order and maintains shared state |
| `app.py` | Provides the Streamlit interface for running the research pipeline |
| `requirements.txt` | Stores project dependencies |
| `.env` | Stores API credentials locally |

---

## ⚙️ Tech Stack

- **Python**
- **LangChain**
- **OpenAI / GPT-4o-mini**
- **Tavily API**
- **BeautifulSoup**
- **Requests**
- **python-dotenv**
- **Streamlit**
- **Rich**

---

## 🔧 Core Components

### 1. Search Agent

The Search Agent uses LangChain's agent framework with the custom `web_search` tool.

It can search for recent information through Tavily and return:

- Titles
- URLs
- Search snippets
- Relevant web sources

```python
search_agent = build_search_agent()
```

---

### 2. Web Search Tool

The `web_search` tool connects the agent to Tavily.

```python
@tool
def web_search(query: str) -> str:
    ...
```

This gives the LLM access to external web-search results instead of relying only on its internal knowledge.

---

### 3. Reader Agent

The Reader Agent receives search results and uses the `scrape_url` tool to extract deeper content from a selected web page.

```python
reader_agent = build_reader_agent()
```

The scraping process uses:

- `requests`
- `BeautifulSoup`

and removes common non-content elements such as:

- `<script>`
- `<style>`
- `<nav>`
- `<footer>`

---

### 4. Writer Chain

The Writer Chain uses LangChain Expression Language (LCEL):

```python
writer_chain = writer_prompt | llm | StrOutputParser()
```

It transforms the collected research into a structured report containing:

- Introduction
- Key Findings
- Conclusion
- Sources

---

### 5. Critic Chain

The Critic Chain evaluates the generated report.

It returns:

```text
Score: X/10

Strengths:
- ...

Areas to Improve:
- ...

One line verdict:
...
```

This introduces an evaluation stage after generation rather than stopping immediately after the first LLM response.

---

## 🔄 Pipeline Flow

The complete pipeline is controlled by:

```python
run_research_pipeline(topic)
```

### Step 1 — Search

The Search Agent finds recent and relevant information.

```text
Research Topic
      ↓
Search Agent
      ↓
Tavily
      ↓
Search Results
```

### Step 2 — Read

The Reader Agent identifies a relevant source and scrapes deeper content.

```text
Search Results
      ↓
Reader Agent
      ↓
scrape_url
      ↓
Detailed Content
```

### Step 3 — Write

The search results and scraped content are combined and passed to the Writer Chain.

```text
Search Results + Scraped Content
              ↓
         Writer Chain
              ↓
        Research Report
```

### Step 4 — Critique

The generated report is passed to the Critic Chain.

```text
Research Report
      ↓
 Critic Chain
      ↓
Score + Strengths + Improvements
```

---

## 🔐 Environment Setup

Create a virtual environment:

```bash
python -m venv venv
```

Activate it.

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
```

**Never commit `.env` or API keys to GitHub.**

Add this to `.gitignore`:

```gitignore
.env
venv/
__pycache__/
```

---

## ▶️ Running the Project

### Terminal Pipeline

Run:

```bash
python pipeline.py
```

Enter a research topic when prompted:

```text
Enter a research topic:
```

For example:

```text
Latest developments in AI agents
```

The terminal will show the progress of each stage.

---

## 🖥️ Streamlit Interface

The project also includes a visual interface through `app.py`.

Run:

```bash
streamlit run app.py
```

The interface allows the user to:

1. Enter a research topic.
2. Start the research pipeline.
3. Track the Search Agent.
4. Track the Reader Agent.
5. Track the Writer Chain.
6. Track the Critic Chain.
7. View the final research output.

---

## ✨ Example Use Cases

ResearchMind can be used for topics such as:

- AI and LLM research
- Technology trends
- Scientific topics
- Software engineering topics
- Market/industry research
- Emerging technologies
- Comparing technical concepts

Example:

```text
Research Topic:
"Latest developments in AI agents"
```

The system searches the web, reads a source, generates a report, and evaluates the report.

---

## 🎯 What This Project Demonstrates

This project goes beyond a basic LLM chatbot and demonstrates several important AI Engineering concepts:

- LLM integration
- LangChain agents
- Custom tools
- Tool calling
- Web search integration
- Web scraping
- Prompt engineering
- LCEL pipelines
- Multi-stage AI workflows
- Shared pipeline state
- LLM-based evaluation
- Streamlit AI application development
- Environment variable management
- External API integration

---

## 🧪 Current Limitations

The current implementation is intentionally focused on learning the fundamentals of agentic workflows.

Some limitations include:

- The Reader Agent primarily works with a selected URL rather than systematically reading multiple sources.
- The Critic Chain evaluates the report but does not automatically send its feedback back to the Writer for another revision.
- Web scraping depends on the structure and accessibility of the target website.
- Scraped content is truncated, so very long pages are not fully processed.
- Source verification is not performed independently before the final report is generated.
- The pipeline is sequential rather than parallel.

These limitations also provide clear directions for future improvements.

---

## 🚀 Future Improvements

Possible next versions could include:

- 🔁 Writer → Critic → Writer iterative refinement
- 📚 Multi-source research instead of a single scraped page
- ⚡ Parallel research agents
- 🧠 Memory / persistent research state
- 📑 Citation validation
- 🔍 Source quality evaluation
- 🗄️ Vector database integration
- 📄 PDF/document ingestion
- 🧩 LangGraph-based orchestration
- 🛡️ Better error handling and retries
- 📊 Research history and report storage
- 🚀 Production deployment
- 🔐 Improved secret and configuration management
- 🧪 Automated evaluation tests

---

## 📌 Important Code Note

The repository screenshot shows `agents.py`, while the pasted code is labelled `agent.py`.

The import in `pipeline.py` is:

```python
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain
```

Therefore, the file should be named:

```text
agents.py
```

unless the import is changed accordingly.

Also, the test call at the bottom of `tools.py`:

```python
print(scrape_url.invoke("https://github.com/connectwithaadi?tab=repositories"))
```

should ideally be removed or placed under a separate test block, because importing `tools.py` will otherwise execute the scraping request immediately.

---

## 🏗️ Learning Architecture

The project represents a useful progression from a simple LLM application toward **Agentic AI Engineering**:

```text
LLM
 ↓
Prompt Engineering
 ↓
LLM Chains
 ↓
Tools
 ↓
Agents
 ↓
Multi-Agent Workflow
 ↓
Evaluation / Critic
 ↓
Agentic AI Application
```

This makes ResearchMind a solid hands-on project for understanding how LLMs can interact with tools and collaborate through a structured workflow.

---

## 👨‍💻 Author

Built as part of an **AI Engineering / Generative AI learning journey**.

---

## ⭐ If You Found This Useful

Consider starring the repository and exploring the implementation to understand how LangChain agents, custom tools, web search, scraping, and LLM chains can be combined into an end-to-end AI research workflow.
