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
        from config import settings
        parts: list[str] = []

        # Use config-driven limits (default: MAX_CONTEXT_CHUNKS=8)
        for document in state.get("reranked_results", [])[:settings.MAX_CONTEXT_CHUNKS]:
            text = document.get("text", "")
            if text:
                parts.append(text)

        # Include top graph results for enriched context
        for item in state.get("graph_results", [])[:5]:
            if isinstance(item, dict):
                parts.append(str(item))

        context = "\n\n".join(parts)
        # Hard cap at MAX_PROMPT_TOKENS chars (default: 6000 chars ≈ 1500 tokens)
        # Increased to 20000 for detailed answers while still being below LLM limits
        return context[:20000]

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