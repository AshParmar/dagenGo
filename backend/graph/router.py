from typing import TypedDict, Any


class DagenGoState(TypedDict, total=False):

    # ==========================================================
    # User
    # ==========================================================

    query: str
    language: str

    # ==========================================================
    # Planner
    # ==========================================================

    plan: dict

    query_type: str
    retrieval_strategy: str

    web_search: bool
    graph_retrieval: bool
    multilingual: bool
    decompose: bool

    # ==========================================================
    # Query Processing
    # ==========================================================

    rewritten_query: str
    multilingual_queries: list[str]
    multi_queries: list[str]

    # ==========================================================
    # Web Search
    # ==========================================================

    retrieved_documents: list[dict]

    # ==========================================================
    # Chunking
    # ==========================================================

    chunks: list[dict]

    # ==========================================================
    # Knowledge Graph
    # ==========================================================

    entities: list[dict]
    relations: list[dict]

    # ==========================================================
    # Retrieval
    # ==========================================================

    dense_results: list[dict]
    sparse_results: list[dict]
    graph_results: list[dict]

    merged_results: list[dict]
    reranked_results: list[dict]

    # ==========================================================
    # Generation
    # ==========================================================

    answer: str

    # ==========================================================
    # Verification
    # ==========================================================

    verification: dict

    # ==========================================================
    # Evaluation
    # ==========================================================

    hallucination: dict
    confidence: dict
    groundedness: dict

    # ==========================================================
    # Reflection
    # ==========================================================

    reflection: dict

    next_action: str
    improved_query: str

    # ==========================================================
    # Judge
    # ==========================================================

    approved: bool
    judge_reason: str

    final_answer: str

    # ==========================================================
    # Metadata
    # ==========================================================

    retry_count: int

    citations: list[dict]

    metadata: dict[str, Any]