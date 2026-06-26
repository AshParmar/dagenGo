from langchain_core.output_parsers import JsonOutputParser

from graph.state import DagenGoState
from llm.models import gemini_llm
from llm.prompts.multilingual import multilingual_prompt


class MultilingualRetriever:

    def __init__(self):
        self.chain = (
            multilingual_prompt
            | gemini_llm
            | JsonOutputParser()
        )

    def generate_queries(
        self,
        state: DagenGoState
    ) -> DagenGoState:

        result = self.chain.invoke(
            {
                "query": state["rewritten_query"],
                "language": state["language"],
            }
        )

        state["multilingual_queries"] = result["queries"]

        return state