from langchain_core.output_parsers import StrOutputParser

from llm.models import gemini_llm
from llm.prompts.reasoning import reasoning_prompt


class ReasoningAgent:

    def __init__(self):

        self.chain = (
            reasoning_prompt
            | gemini_llm
            | StrOutputParser()
        )

    def invoke(self, state):

        answer = self.chain.invoke(
            {
                "query": state["query"],
                "context": state["context"]
            }
        )

        state["answer"] = answer

        return state