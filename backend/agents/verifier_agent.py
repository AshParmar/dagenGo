from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from graph.state import DagenGoState
from llm.models import gemini_llm


verifier_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are DagenGo's Evidence Verification Agent.

Given:
1. User Query
2. Retrieved Evidence
3. Generated Answer

Determine:

- Are all claims supported?
- Which claims are unsupported?
- Is the evidence sufficient?

Return ONLY JSON.

{{
    "supported": true,
    "supported_claims": [],
    "unsupported_claims": [],
    "missing_information": [],
    "needs_reretrieval": false
}}
"""
        ),
        (
            "human",
            """
Query:
{query}

Evidence:
{evidence}

Answer:
{answer}
"""
        ),
    ]
)


class VerifierAgent:

    def __init__(self):

        self.chain = (
            verifier_prompt
            | gemini_llm
            | JsonOutputParser()
        )

    def invoke(
        self,
        state: DagenGoState,
    ) -> DagenGoState:

        verification = self.chain.invoke(
            {
                "query": state["query"],
                "evidence": state["reranked_results"][:5],
                "answer": state.get("answer", "")[:4000],
            }
        )

        if isinstance(verification, list) and len(verification) > 0:
            verification = verification[0]

        if not isinstance(verification, dict):
            verification = {}

        state["verification"] = verification

        state["supported"] = bool(verification.get("supported", False))

        state["needs_reretrieval"] = bool(verification.get("needs_reretrieval", False))

        return state