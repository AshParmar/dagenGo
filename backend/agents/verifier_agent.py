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

{
    "supported": true,
    "supported_claims": [],
    "unsupported_claims": [],
    "missing_information": [],
    "needs_reretrieval": false
}
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
                "evidence": state["reranked_results"],
                "answer": state["answer"],
            }
        )

        state["verification"] = verification

        state["supported"] = verification["supported"]

        state["needs_reretrieval"] = verification["needs_reretrieval"]

        return state