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

{
    "query_type": "",
    "retrieval_strategy": "",
    "multilingual": false,
    "web_search": false,
    "graph_retrieval": false,
    "decompose": false
}
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

        state["plan"] = plan

        state["query_type"] = plan["query_type"]

        state["retrieval_strategy"] = plan["retrieval_strategy"]

        state["multilingual"] = plan["multilingual"]

        state["web_search"] = plan["web_search"]

        state["graph_retrieval"] = plan["graph_retrieval"]

        state["decompose"] = plan["decompose"]

        return state