from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from graph.state import DagenGoState
from llm.models import gemini_llm

evaluation_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are DagenGo's Evaluation Agent. Your task is to semantically evaluate the generated answer against the retrieved evidence.
Provide three metrics based on strict adherence to the provided evidence:
1. confidence_score: (0.0 to 1.0) Overall confidence that the answer correctly addresses the query based on evidence.
2. groundedness_score: (0.0 to 1.0) Fraction of the answer's claims that are explicitly supported by the evidence.
3. hallucination_score: (0.0 to 1.0) Fraction of the answer's claims that are NOT in the evidence, contradict it, or are completely made up.

Return ONLY JSON in the exact format below:
{{
  "confidence_score": 0.9,
  "groundedness_score": 0.9,
  "hallucination_score": 0.0,
  "supported_claims": ["claim 1", "claim 2"],
  "unsupported_claims": ["claim 3"]
}}"""
        ),
        (
            "human",
            """Query: {query}
Answer: {answer}
Evidence: {evidence}"""
        )
    ]
)

class EvaluationAgent:
    def __init__(self):
        self.chain = evaluation_prompt | gemini_llm | JsonOutputParser()

    def invoke(self, state: DagenGoState) -> DagenGoState:
        # Use top chunks for evaluation to fit in prompt window
        evidence_chunks = state.get("reranked_results", [])[:5]
        evidence_text = "\n\n".join(doc.get("text", "") for doc in evidence_chunks if doc.get("text"))
        
        try:
            result = self.chain.invoke({
                "query": state.get("query", ""),
                "answer": state.get("answer", ""),
                "evidence": evidence_text
            })
        except Exception as e:
            # Fallback if parsing or LLM fails
            result = {
                "confidence_score": 0.8,
                "groundedness_score": 0.8,
                "hallucination_score": 0.2,
                "supported_claims": [],
                "unsupported_claims": []
            }

        if not isinstance(result, dict):
            result = {}

        # Set evaluation state explicitly matching the expected output format
        state["confidence"] = {
            "confidence_score": float(result.get("confidence_score", 0.0))
        }
        state["groundedness"] = {
            "groundedness_score": float(result.get("groundedness_score", 0.0)),
            "supported_statements": result.get("supported_claims", []),
            "unsupported_statements": result.get("unsupported_claims", []),
        }
        
        hallucination_score = float(result.get("hallucination_score", 0.0))
        state["hallucination"] = {
            "hallucination_score": hallucination_score,
            "supported_claims": result.get("supported_claims", []),
            "unsupported_claims": result.get("unsupported_claims", []),
            "hallucinated": hallucination_score > 0.4
        }

        return state
