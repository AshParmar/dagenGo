from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from llm.models import gemini_llm


confidence_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are DagenGo's Confidence Scoring Agent.

Estimate how confident the system should be in the generated answer.

Consider:

- Evidence quality
- Retrieval quality
- Verification results
- Hallucination analysis
- Completeness of answer

Return ONLY valid JSON.

{
    "confidence_score": 0.0,
    "reason": ""
}
"""
        ),
        (
            "human",
            """
Question:
{query}

Answer:
{answer}

Evidence:
{evidence}

Verification:
{verification}

Hallucination Report:
{hallucination}
"""
        ),
    ]
)


class ConfidenceScorer:

    def __init__(self):

        self.chain = (
            confidence_prompt
            | gemini_llm
            | JsonOutputParser()
        )

    def evaluate(
        self,
        query: str,
        answer: str,
        evidence,
        verification,
        hallucination,
    ):

        return self.chain.invoke(
            {
                "query": query,
                "answer": answer,
                "evidence": evidence,
                "verification": verification,
                "hallucination": hallucination,
            }
        )