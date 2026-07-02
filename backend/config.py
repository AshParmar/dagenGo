from dotenv import load_dotenv
import os

load_dotenv()


class Settings:

    # ==========================
    # API Keys
    # ==========================
    GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY")
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY")
    TAVILY_API_KEY: str | None = os.getenv("TAVILY_API_KEY")
    EXA_API_KEY: str | None = os.getenv("EXA_API_KEY")

    # ==========================
    # LLM Models
    # ==========================
    GEMINI_MODEL: str = "gemini-2.5-pro"
    OPENAI_MODEL: str = "gpt-4o-mini"
    CLAUDE_MODEL: str = "claude-3-5-sonnet-latest"

    # ==========================
    # Embedding Model
    # ==========================
    EMBEDDING_MODEL: str = "embedding-001"

    # ==========================
    # Qdrant
    # ==========================
    QDRANT_URL: str | None = os.getenv("QDRANT_URL")
    QDRANT_API_KEY: str | None = os.getenv("QDRANT_API_KEY")
    COLLECTION_NAME: str = "dagengo_local"

    # ==========================
    # Neo4j
    # ==========================
    NEO4J_URI: str | None = os.getenv("NEO4J_URI")
    NEO4J_USERNAME: str | None = os.getenv("NEO4J_USERNAME")
    NEO4J_PASSWORD: str | None = os.getenv("NEO4J_PASSWORD")

    # ==========================
    # Retrieval
    # ==========================
    TOP_K: int = 10
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    RERANK_TOP_K: int = 5

    # ==========================
    # Chunking
    # ==========================
    CHUNK_SIZE: int = 700            # Production: 600-800 tokens
    CHUNK_OVERLAP: int = 120         # Production: 100-150 tokens
    MAX_CONTEXT_CHUNKS: int = 8      # Max chunks sent to reasoning LLM
    MAX_PROMPT_TOKENS: int = 6000    # Hard cap on prompt characters (~1500 tokens)

    # ==========================
    # Knowledge Graph
    # ==========================
    KG_MAX_TEXT_CHARS: int = 6000    # Max chars sent for entity/relation extraction
    KG_CACHE_TTL: int = 3600         # Seconds to keep KG extraction cache entries
    KG_MAX_ENTITIES: int = 20        # Max entities to extract per document
    KG_MAX_RELATIONS: int = 30       # Max relations to extract per document

    # ==========================
    # Planner
    # ==========================
    # When True, use deterministic rule-based planner (sub-1s, no LLM).
    # When False, use LLM planner (slower, used only when query is highly ambiguous).
    PLANNER_USE_RULES: bool = True

    # ==========================
    # Verification
    # ==========================
    # Skip the verifier LLM call when confidence is already high enough
    SKIP_VERIFICATION_CONFIDENCE_THRESHOLD: float = 0.80

    # ==========================
    # Caching
    # ==========================
    SEARCH_CACHE_TTL: int = 300      # Seconds to cache web search results
    EMBED_CACHE_TTL: int = 600       # Seconds to cache embedding vectors


settings = Settings()