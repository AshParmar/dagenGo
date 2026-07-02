from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from graph.state import DagenGoState
from llm.models import gemini_llm


reflection_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are DagenGo's Reflection Agent. Decide the next action based on evaluation metrics.

Actions:
- retrieve_again: fetch new evidence with improved_query (use when hallucination is high or groundedness is low)
- graph_retrieve: get more KG context
- web_search: targeted web search
- continue: proceed (rarely used; judge handles approval)
- abort: only for unresolvable error states

RULE: If judge rejected (Approved=False), choose 'retrieve_again' and write an improved_query.

Return ONLY JSON:
{{"action":"","reason":"","improved_query":""}}""",
        ),
        (
            "human",
            """Query: {query}
Judge: {approved} — {judge_reason}
Confidence={confidence_score} | Groundedness={groundedness_score} | Hallucination={hallucination_score}""",
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

        # If the judge rejected the answer, default to retrying retrieval rather than exiting
        default_action = "continue" if state.get("approved", False) else "retrieve_again"
        state["next_action"] = reflection.get("action", default_action)

        state["improved_query"] = reflection.get("improved_query", "")

        return state