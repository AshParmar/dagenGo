# DagenGo 🌍🔍

> **The Next-Generation Cross-Lingual Research & Fact Verification Agent**

![DagenGo Execution Pipeline](https://via.placeholder.com/1200x400?text=DagenGo+Agentic+Research+Pipeline)

DagenGo is an autonomous, agentic AI research system engineered for absolute factual accuracy, complex multi-step reasoning, and robust verifiability. While standard LLM chatbots rely on internal training data or basic RAG, DagenGo acts like a dedicated human researcher. It orchestrates a sophisticated **LangGraph** pipeline to retrieve live data across the web, cross-check facts, extract relationships into a graph database, and strictly evaluate its own answers before presenting them to the user.

---

## ⚡ Key Features

- **Agentic AI Workflow:** DagenGo isn't just one prompt. It utilizes specialized, modular agents (Planner, Reasoner, Verifier, Evaluator, Judge, Reflector) that collaborate, critique, and synthesize information autonomously.
- **Hybrid RAG Retrieval:** Fuses **Dense vector embeddings** (via Qdrant) with **Sparse keyword search** (BM25) and **Live Web Search** (Exa/Tavily APIs) to ensure zero context is missed.
- **Real-Time Knowledge Graph (GraphRAG):** Automatically extracts entities and complex relationships from retrieved documents into a **Neo4j** database. This allows the reasoning agent to traverse logical connections that traditional vector search misses.
- **Cross-Lingual Native:** Break language barriers. Submit a query in one language (e.g., Hindi, Japanese), and DagenGo will conduct its research across global English sources, process the data, and output a verified, structured markdown response back in your native language.
- **Aggressive Self-Evaluation:** Emits strict, LLM-graded metrics for **Confidence**, **Groundedness**, and **Hallucination**. If the answer fails verification, the Judge agent halts the output and triggers the Reflection agent to re-strategize and search again.

---

## 🏗️ Deep Dive Architecture

### Backend Stack
- **FastAPI:** High-performance, asynchronous REST/SSE server powering the streaming responses.
- **LangGraph & LangChain:** Orchestrates the multi-agent state graph, allowing looping, conditional edges, and robust memory management.
- **Dynamic LLM Engine:** Supports routing requests to Gemini, Claude, OpenAI, or fully local models via Ollama (Llama 3).
- **Neo4j:** The graph database layer responsible for dynamic Entity-Relationship extraction and GraphRAG retrieval.
- **Qdrant:** High-speed, high-dimensional vector database for semantic Dense retrieval.
- **Exa & Tavily:** Premium integrations for live web search, data scraping, and news retrieval.

### Frontend Stack
- **React 19 & TypeScript:** Scalable, type-safe UI architecture.
- **TanStack Router:** Type-safe, file-based routing mechanism.
- **TailwindCSS & Framer Motion:** Delivers a dynamic, premium, glassmorphism-inspired aesthetic with highly interactive micro-animations.
- **Zustand:** Fast, light-weight, and persistent state management for research session history.
- **Server-Sent Events (SSE):** Renders the agent's thought process, real-time pipeline execution, and markdown answer token-by-token.

---

## 🧠 The Agent Pipeline Lifecycle

When a user submits a query, DagenGo executes the following LangGraph lifecycle:

1. **Language Detection:** Identifies the user's input language dynamically.
2. **Planner Agent:** Analyzes the complexity of the query to determine the best retrieval strategy (Web Search vs Graph Retrieval vs Hybrid).
3. **Query Rewrite Agent:** Expands and optimizes the prompt for search engines to maximize hit rates.
4. **Retrieval Wrapper:** Executes Multi-Query generation, runs concurrent Hybrid Retrieval (Dense & Sparse), and queries live Web Search APIs (with TTL caching).
5. **Knowledge Graph Builder:** Parses retrieved chunks, extracts named entities and relational edges, and merges them into Neo4j in real-time.
6. **Reasoning Agent:** Generates a highly detailed, deeply researched markdown report strictly bound by the provided evidence window.
7. **Verifier Agent:** Cross-checks if the generated answer directly satisfies the initial user query constraints.
8. **Evaluation Agent:** Grades the response using strict LLM-based hallucination and groundedness checks.
9. **Judge Agent:** Acts as the final gatekeeper. Approves the final response to stream to the user, OR rejects it and triggers the **Reflection Agent** to retry and gather missing data.

---

## 🚀 Getting Started

### 📋 Prerequisites
Before running DagenGo, ensure you have the following installed:
- **Python 3.11+**
- **Node.js 18+**
- **Neo4j Database** (Local Desktop instance or AuraDB cloud)
- API Keys for your preferred LLM provider (e.g., Google Gemini), Exa, and Tavily.

### ⚙️ Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```
2. **Create a virtual environment & install dependencies:**
   ```bash
   python -m venv venv
   # On Windows: venv\Scripts\activate
   # On Mac/Linux: source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Configure Environment Variables:**
   Copy the sample environment file and add your sensitive credentials:
   ```bash
   cp .env.example .env
   ```
   *Required Variables in `.env`:*
   - `GEMINI_API_KEY` (or OpenAI/Anthropic)
   - `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`
   - `EXA_API_KEY`
   - `TAVILY_API_KEY`

4. **Start the FastAPI server:**
   ```bash
   uvicorn main:app --port 8000 --reload
   ```

### 💻 Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```
2. **Install node modules:**
   ```bash
   npm install
   ```
3. **Start the Vite development server:**
   ```bash
   npm run dev
   ```

Open your browser to `http://localhost:5173/` (or the port Vite provides) to start your first agentic research session!

---

## 🤝 Contributing
Contributions are highly encouraged! If you're interested in improving the Knowledge Graph extraction latency, adding new LLM providers, or building out the UI Graph visualization component, please open a pull request.

## 📄 License
This project is licensed under the MIT License. See the `LICENSE` file for more details.
