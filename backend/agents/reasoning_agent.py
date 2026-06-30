from langchain_core.output_parsers import StrOutputParser

from graph.state import DagenGoState
from llm.models import gemini_llm
from llm.prompts.reasoning import reasoning_prompt


class ReasoningAgent:

    def __init__(self):

        self.chain = (
            reasoning_prompt
            | gemini_llm
            | StrOutputParser()
        )

    def _build_context(self, state: DagenGoState) -> str:
        parts: list[str] = []

        for document in state.get("reranked_results", []):
            text = document.get("text", "")
            if text:
                parts.append(text)

        for item in state.get("graph_results", []):
            if isinstance(item, dict):
                parts.append(str(item))

        return "\n\n".join(parts)

    def invoke(self, state: DagenGoState) -> DagenGoState:

        context = self._build_context(state)

        answer = self.chain.invoke(
            {
                "query": state["query"],
                "context": context,
            }
        )

        state["answer"] = answer

        return state