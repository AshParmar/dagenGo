from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from graph.state import DagenGoState
from llm.models import gemini_llm


planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are DagenGo's Planner Agent.

Analyze the user's query and decide the execution strategy.

Return ONLY valid JSON.

{{
    "query_type": "",
    "retrieval_strategy": "",
    "multilingual": false,
    "web_search": false,
    "graph_retrieval": false,
    "decompose": false
}}
"""
        ),
        (
            "human",
            """
Query:
{query}
"""
        ),
    ]
)


class PlannerAgent:

    def __init__(self):

        self.chain = (
            planner_prompt
            | gemini_llm
            | JsonOutputParser()
        )

    def invoke(
        self,
        state: DagenGoState,
    ) -> DagenGoState:

        plan = self.chain.invoke(
            {
                "query": state["query"],
            }
        )

        if isinstance(plan, list) and len(plan) > 0:
            plan = plan[0]

        if not isinstance(plan, dict):
            plan = {}

        state["plan"] = plan

        state["query_type"] = plan.get("query_type", "general")

        state["retrieval_strategy"] = plan.get("retrieval_strategy", "hybrid")

        state["multilingual"] = bool(plan.get("multilingual", False))

        state["web_search"] = bool(plan.get("web_search", True))

        state["graph_retrieval"] = bool(plan.get("graph_retrieval", True))

        state["decompose"] = bool(plan.get("decompose", False))

        return state