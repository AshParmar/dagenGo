"""
Multi-Query Retriever — Optimized deterministic variant.

Replaces the LLM-based multi-query generator with a fast rule-based approach
that generates query variants in <1ms with no LLM call.

Variants generated:
  1. Original rewritten query
  2. Question form (adds "What is" / "Explain" prefix)
  3. Keywords only (strip stop words)
  4. Broader context (add "overview" / "background")
  5. Specific detail (add "detailed" prefix)

Expected latency improvement: eliminates one full LLM round-trip (~5-8s)
"""
import re
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from config import settings
from graph.state import DagenGoState
from llm.models import gemini_llm

logger = logging.getLogger(__name__)

# LLM multi-query prompt — kept as fallback only
_multi_query_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            'Generate 3 search query variants for the given query. Return ONLY JSON: {{"queries":["...","...","..."]}}',
        ),
        ("human", "{query}"),
    ]
)

_STOP_WORDS = frozenset({
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "to", "of", "in", "on", "at", "by",
    "for", "with", "about", "as", "into", "through", "and", "or", "but",
    "if", "when", "where", "who", "what", "how", "why", "which", "that",
    "this", "these", "those",
})


def _keywords_only(query: str) -> str:
    words = re.findall(r"\b\w{3,}\b", query)
    keywords = [w for w in words if w.lower() not in _STOP_WORDS]
    return " ".join(keywords) if keywords else query


def _generate_rule_based_queries(query: str) -> list[str]:
    """Generate 5 query variants deterministically in <1ms."""
    q = query.strip()
    keywords = _keywords_only(q)

    variants = [
        q,
        f"What is {q}" if not q.lower().startswith("what") else f"Explain {q}",
        keywords,
        f"{q} overview background context",
        f"detailed information about {q}",
    ]

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for v in variants:
        normalized = v.strip().lower()
        if normalized not in seen and normalized:
            seen.add(normalized)
            unique.append(v.strip())

    return unique[:5]


class MultiQueryRetriever:

    def __init__(self) -> None:
        self._chain = _multi_query_prompt | gemini_llm | JsonOutputParser()

    def generate(self, state: DagenGoState) -> DagenGoState:
        query = state.get("rewritten_query") or state.get("query", "")

        # Always use the fast rule-based path
        queries = _generate_rule_based_queries(query)
        logger.debug("Multi-query (rule-based): %d variants for '%s'", len(queries), query[:60])

        state["multi_queries"] = queries
        return state