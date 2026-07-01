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

        # Limit to top 5 reranked results max
        for document in state.get("reranked_results", [])[:5]:
            text = document.get("text", "")
            if text:
                parts.append(text)

        # Limit to top 5 graph results max
        for item in state.get("graph_results", [])[:5]:
            if isinstance(item, dict):
                parts.append(str(item))

        context = "\n\n".join(parts)
        # Limit to 12,000 characters max
        return context[:12000]

    def invoke(self, state: DagenGoState) -> DagenGoState:

        context = self._build_context(state)

        # Use the auto-detected language from the language_node stage
        language = state.get("language") or "English"

        answer = self.chain.invoke(
            {
                "query": state["query"],
                "context": context,
                "language": language,
            }
        )

        state["answer"] = answer

        return state