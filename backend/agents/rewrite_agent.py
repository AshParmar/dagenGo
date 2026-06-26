from langchain_core.output_parsers import StrOutputParser

from graph.state import DagenGoState
from llm.models import gemini_llm
from llm.prompts.rewrite_prompts import rewrite_prompt


class RewriteAgent:

    def __init__(self):
        self.chain = (
            rewrite_prompt
            | gemini_llm
            | StrOutputParser()
        )

    def invoke(self, state: DagenGoState) -> DagenGoState:

        rewritten_query = self.chain.invoke(
            {
                "query": state["query"],
                "language": state["language"],
            }
        )

        state["rewritten_query"] = rewritten_query

        return state