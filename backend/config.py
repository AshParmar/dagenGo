from dotenv import load_dotenv
import os

load_dotenv()


class Settings:

    # ==========================
    # API Keys
    # ==========================
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    EXA_API_KEY = os.getenv("EXA_API_KEY")

    # ==========================
    # LLM Models
    # ==========================
    GEMINI_MODEL = "gemini-2.5-pro"
    OPENAI_MODEL = "gpt-4o-mini"
    CLAUDE_MODEL = "claude-3-5-sonnet-latest"

    # ==========================
    # Embedding Model
    # ==========================
    EMBEDDING_MODEL = "embedding-001"

    # ==========================
    # Qdrant
    # ==========================
    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    COLLECTION_NAME = "dagengo_local"

    # ==========================
    # Neo4j
    # ==========================
    NEO4J_URI = os.getenv("NEO4J_URI")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

    # ==========================
    # Retrieval
    # ==========================
    TOP_K = 10
    RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    RERANK_TOP_K = 5


settings = Settings()