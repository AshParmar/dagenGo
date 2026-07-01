import re
from langchain_core.output_parsers import StrOutputParser

from graph.state import DagenGoState
from llm.models import gemini_llm
from llm.prompts.rewrite_prompts import rewrite_prompt


def clean_rewritten_query(text: str) -> str:
    """Extract and sanitize the core query to bypass LLM conversational text and prevent API errors."""
    text = text.strip()
    
    # 1. Look for quotes first (across the entire text)
    quotes = re.findall(r'"([^"]+)"', text)
    if quotes:
        text = max(quotes, key=len)
    else:
        single_quotes = re.findall(r"'([^']+)'", text)
        if single_quotes:
            text = max(single_quotes, key=len)
        elif "\n" in text:
            # 2. If no quotes, split by newlines and filter out conversational preamble lines
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            prefixes = [
                "rewritten query:", "improved query:", "here is the rewritten query:",
                "here is the improved query:", "search query:", "proposed query:",
                "here is a rewritten version:", "here is the search query:",
                "sure, here is", "here is the query:"
            ]
            if lines:
                first_line_lower = lines[0].lower()
                if any(first_line_lower.startswith(p) or first_line_lower.endswith(":") for p in prefixes) and len(lines) > 1:
                    text = lines[1]
                else:
                    text = lines[0]
            
    # 3. Strip common conversational prefixes from the resulting query
    prefixes = [
        "rewritten query:", "improved query:", "here is the rewritten query:",
        "here is the improved query:", "search query:", "proposed query:",
        "here is a rewritten version:", "here is the search query:",
        "संशोधित प्रश्न:", "संशोधित क्वेरी:"
    ]
    
    cleaned = text.lower()
    for prefix in prefixes:
        if cleaned.startswith(prefix):
            text = text[len(prefix):].strip()
            break
            
    # Clean surrounding quotes/markdown/spaces
    text = text.strip('`"\'* \n\t')
    
    # Cap length to 200 characters to prevent Tavily/Exa query length limit errors
    return text[:200]


class RewriteAgent:

    def __init__(self):
        self.chain = (
            rewrite_prompt
            | gemini_llm
            | StrOutputParser()
        )

    def invoke(self, state: DagenGoState) -> DagenGoState:
        # Use improved_query from reflection if present, otherwise use original query
        query_source = state.get("improved_query") or state["query"]

        rewritten_query = self.chain.invoke(
            {
                "query": query_source,
                "language": state["language"],
            }
        )

        state["rewritten_query"] = clean_rewritten_query(rewritten_query)

        return state