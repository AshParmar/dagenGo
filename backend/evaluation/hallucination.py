from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from llm.models import gemini_llm


hallucination_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are DagenGo's Hallucination Detection Agent.

Compare the generated answer ONLY against the provided evidence.

Determine:

1. Which claims are fully supported.
2. Which claims are partially supported.
3. Which claims are unsupported.
4. Estimate hallucination risk.

Return ONLY valid JSON.

{
    "hallucination_score": 0.0,
    "supported_claims": [],
    "partial_claims": [],
    "unsupported_claims": [],
    "hallucinated": false
}
"""
        ),
        (
            "human",
            """
Question:
{query}

Evidence:
{evidence}

Answer:
{answer}
"""
        ),
    ]
)


class HallucinationDetector:

    def __init__(self):

        self.chain = (
            hallucination_prompt
            | gemini_llm
            | JsonOutputParser()
        )

    def evaluate(
        self,
        query: str,
        answer: str,
        evidence,
    ):

        return self.chain.invoke(
            {
                "query": query,
                "answer": answer,
                "evidence": evidence,
            }
        )