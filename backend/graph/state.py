from typing import TypeDict

class DagenGoState(TypedDict):
    """
    Shared state passed between all LangGraph nodes.
    Every node can read from and update this state.
    """

    # ==========================
    # User Input
    # ==========================
    query: str
    language: str

    # ==========================
    # Planning
    # ==========================
    intent: Optional[str]
    rewritten_query: Optional[str]
    multilingual_queries: Optional[List[str]]

    # ==========================
    # Retrieval
    # ==========================
    vector_documents: Optional[List[Dict[str, Any]]]
    bm25_documents: Optional[List[Dict[str, Any]]]
    graph_documents: Optional[List[Dict[str, Any]]]

    merged_documents: Optional[List[Dict[str, Any]]]
    reranked_documents: Optional[List[Dict[str, Any]]]

    context: Optional[str]

    # ==========================
    # Reasoning
    # ==========================
    answer: Optional[str]

    # ==========================
    # Verification
    # ==========================
    extracted_claims: Optional[List[str]]
    supported_claims: Optional[List[str]]
    unsupported_claims: Optional[List[str]]
    contradictions: Optional[List[str]]

    # ==========================
    # Evaluation
    # ==========================
    hallucination_score: Optional[float]
    groundedness_score: Optional[float]
    confidence_score: Optional[float]

    # ==========================
    # Reflection
    # ==========================
    reflection: Optional[str]
    retry_count: int

    # ==========================
    # Final Output
    # ==========================
    citations: Optional[List[str]]
    final_answer: Optional[str]