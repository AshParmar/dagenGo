from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from graph.state import DagenGoState
from llm.models import gemini_llm


reflection_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are DagenGo's Reflection Agent.

Analyze the verification report, evaluation metrics, and the judge's feedback to decide the next action.

Possible actions:

- continue (use when answer is approved and no further action is needed)
- retrieve_again (use to search web/sources again with an improved query)
- graph_retrieve (use to fetch more context from the knowledge graph)
- web_search (use to perform web search)
- ask_user (use only if query is completely nonsensical or unresolvable)
- abort (use only for error states)

IMPORTANT: If the judge rejected the answer (Approved: False) due to high hallucination or low groundedness, you MUST choose 'retrieve_again' or 'web_search' to fetch better, more accurate evidence. Propose a targeted search query in 'improved_query' focused on finding the correct information.

Return ONLY JSON.

{{
    "action":"",
    "reason":"",
    "improved_query":""
}}
"""
        ),
        (
            "human",
            """
User Query:
{query}

Verification Report:
{verification}

Evaluation Metrics:
- Confidence Score: {confidence_score}
- Groundedness Score: {groundedness_score}
- Hallucination Score: {hallucination_score}

Judge Approval: {approved}
Judge Reason: {judge_reason}
"""
        ),
    ]
)


class ReflectionAgent:

    def __init__(self):

        self.chain = (
            reflection_prompt
            | gemini_llm
            | JsonOutputParser()
        )

    def invoke(
        self,
        state: DagenGoState,
    ) -> DagenGoState:

        reflection = self.chain.invoke(
            {
                "query": state["query"],
                "verification": state["verification"],
                "confidence_score": f"{state.get('confidence', {}).get('confidence_score', 0.0) * 100:.0f}%",
                "groundedness_score": f"{state.get('groundedness', {}).get('groundedness_score', 0.0) * 100:.0f}%",
                "hallucination_score": f"{state.get('hallucination', {}).get('hallucination_score', 0.0) * 100:.0f}%",
                "approved": str(state.get("approved", False)),
                "judge_reason": state.get("judge_reason", ""),
            }
        )

        if isinstance(reflection, list) and len(reflection) > 0:
            reflection = reflection[0]

        if not isinstance(reflection, dict):
            reflection = {}

        state["reflection"] = reflection

        state["next_action"] = reflection.get("action", "continue")

        state["improved_query"] = reflection.get("improved_query", "")

        return state