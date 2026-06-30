from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from llm.models import gemini_llm


groundedness_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are DagenGo's Groundedness Evaluator.

Determine how well the generated answer is grounded in the provided evidence.

Evaluate:

1. Groundedness score (0-1)
2. Supported statements
3. Unsupported statements

Return ONLY valid JSON.

{
    "groundedness_score":0.0,
    "supported_statements":[],
    "unsupported_statements":[]
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


class GroundednessEvaluator:

    def __init__(self):

        self.chain = (
            groundedness_prompt
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