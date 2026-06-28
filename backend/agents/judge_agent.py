from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from graph.state import DagenGoState
from llm.models import gemini_llm


judge_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are DagenGo's Final Judge.

Review the entire pipeline.

Evaluate:

1. Is the answer correct?
2. Is every important claim supported?
3. Is confidence high?
4. Is hallucination risk acceptable?

Return ONLY JSON.

{
    "approved": true,
    "reason": "",
    "final_answer": ""
}
"""
        ),
        (
            "human",
            """
Query:
{query}

Answer:
{answer}

Evidence:
{evidence}

Verification:
{verification}
"""
        ),
    ]
)


class JudgeAgent:

    def __init__(self):

        self.chain = (
            judge_prompt
            | gemini_llm
            | JsonOutputParser()
        )

    def invoke(
        self,
        state: DagenGoState,
    ) -> DagenGoState:

        result = self.chain.invoke(
            {
                "query": state["query"],
                "answer": state["answer"],
                "evidence": state["reranked_results"],
                "verification": state["verification"],
            }
        )

        state["approved"] = result["approved"]

        state["judge_reason"] = result["reason"]

        state["final_answer"] = result["final_answer"]

        return state