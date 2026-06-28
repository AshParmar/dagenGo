from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from graph.state import DagenGoState
from llm.models import gemini_llm


multi_query_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are DagenGo's Multi Query Generator.

Generate 5 diverse retrieval queries that preserve the user's intent.

Rules:
- Different wording
- Different terminology
- Same meaning
- Do NOT answer the question

Return ONLY JSON.

{
    "queries":[
        "...",
        "...",
        "...",
        "...",
        "..."
    ]
}
"""
        ),
        (
            "human",
            """
Original Query:

{query}
"""
        ),
    ]
)


class MultiQueryRetriever:

    def __init__(self):

        self.chain = (
            multi_query_prompt
            | gemini_llm
            | JsonOutputParser()
        )

    def generate(
        self,
        state: DagenGoState,
    ) -> DagenGoState:

        result = self.chain.invoke(
            {
                "query": state["rewritten_query"]
            }
        )

        state["multi_queries"] = result["queries"]

        return state