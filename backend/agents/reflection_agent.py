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

Analyze the verification report and decide the next action.

Possible actions:

- continue
- retrieve_again
- graph_retrieve
- web_search
- ask_user
- abort

Return ONLY JSON.

{
    "action":"",
    "reason":"",
    "improved_query":""
}
"""
        ),
        (
            "human",
            """
User Query:
{query}

Verification:
{verification}
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
            }
        )

        state["reflection"] = reflection

        state["next_action"] = reflection["action"]

        state["improved_query"] = reflection["improved_query"]

        return state