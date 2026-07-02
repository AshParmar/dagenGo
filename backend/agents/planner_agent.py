"""
Planner Agent — Optimized for sub-1s latency.

Strategy:
  1. Fast rule-based planner (default, PLANNER_USE_RULES=True):
     Deterministically classifies the query using keyword heuristics in <5ms.
     No LLM call required for the vast majority of queries.

  2. LLM planner (fallback, PLANNER_USE_RULES=False or ambiguous edge cases):
     Uses a minimal single-shot prompt to classify the query.

Expected latency improvement: 17s → <1s
"""
import re
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from config import settings
from graph.state import DagenGoState
from llm.models import gemini_llm

logger = logging.getLogger(__name__)

# Minimal LLM prompt — only used as fallback
planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Classify the query. Return ONLY valid JSON, nothing else.
{{"query_type":"general|factual|comparison|technical","web_search":true,"graph_retrieval":true}}""",
        ),
        ("human", "{query}"),
    ]
)

# ---------------------------------------------------------------------------
# Keyword signals for rule-based classification
# ---------------------------------------------------------------------------
_FACTUAL_PATTERNS = re.compile(
    r"\b(who|what|when|where|how many|how much|which|define|definition|meaning|capital|"
    r"population|year|date|born|died|founded|invented|discovered|created|"
    r"vs\b|versus|winner|champion|score|result|match|fight|battle)\b",
    re.IGNORECASE,
)
_COMPARISON_PATTERNS = re.compile(
    r"\b(compare|comparison|difference|vs|versus|better|worse|pros|cons|"
    r"advantages|disadvantages|similar|different)\b",
    re.IGNORECASE,
)
_TECHNICAL_PATTERNS = re.compile(
    r"\b(how to|tutorial|implement|code|algorithm|architecture|model|"
    r"framework|library|api|install|configure|setup|debug|error|fix|"
    r"build|deploy|train|fine-tune|llm|transformer|neural|python|"
    r"javascript|typescript|docker|kubernetes)\b",
    re.IGNORECASE,
)
_NEWS_PATTERNS = re.compile(
    r"\b(latest|recent|news|today|this week|this year|2024|2025|2026|"
    r"announce|release|update|launch|breaking)\b",
    re.IGNORECASE,
)
_GRAPH_SIGNALS = re.compile(
    r"\b(relationship|connection|link|network|related|association|"
    r"built by|founded by|developed by|author|company|organization)\b",
    re.IGNORECASE,
)


def _rule_based_plan(query: str) -> dict:
    """Return a plan dict in <5ms using keyword heuristics. No LLM call."""
    q = query.strip()

    is_comparison = bool(_COMPARISON_PATTERNS.search(q))
    is_technical = bool(_TECHNICAL_PATTERNS.search(q))
    is_news = bool(_NEWS_PATTERNS.search(q))
    is_factual = bool(_FACTUAL_PATTERNS.search(q))
    needs_graph = bool(_GRAPH_SIGNALS.search(q))

    if is_comparison:
        query_type = "comparison"
        retrieval_strategy = "hybrid"
        graph_retrieval = True
    elif is_technical:
        query_type = "technical"
        retrieval_strategy = "dense"
        graph_retrieval = needs_graph
    elif is_news:
        query_type = "news"
        retrieval_strategy = "web"
        graph_retrieval = False
    elif is_factual:
        query_type = "factual"
        retrieval_strategy = "hybrid"
        graph_retrieval = needs_graph
    else:
        query_type = "general"
        retrieval_strategy = "hybrid"
        graph_retrieval = needs_graph

    return {
        "query_type": query_type,
        "retrieval_strategy": retrieval_strategy,
        "multilingual": False,
        "web_search": True,
        "graph_retrieval": graph_retrieval,
        "decompose": False,
    }


class PlannerAgent:

    def __init__(self) -> None:
        self._chain = (
            planner_prompt
            | gemini_llm
            | JsonOutputParser()
        )

    def _llm_plan(self, query: str) -> dict:
        """Fallback: call LLM with minimal prompt."""
        try:
            result = self._chain.invoke({"query": query})
            if isinstance(result, list) and result:
                result = result[0]
            if not isinstance(result, dict):
                result = {}
            return result
        except Exception as exc:
            logger.warning("LLM planner failed: %s — using rule-based fallback", exc)
            return {}

    def invoke(self, state: DagenGoState) -> DagenGoState:
        query = state["query"]

        if settings.PLANNER_USE_RULES:
            plan = _rule_based_plan(query)
            logger.debug("Rule-based plan: %s", plan)
        else:
            plan = self._llm_plan(query)
            if not plan:
                plan = _rule_based_plan(query)

        state["plan"] = plan
        state["query_type"] = plan.get("query_type", "general")
        state["retrieval_strategy"] = plan.get("retrieval_strategy", "hybrid")
        state["multilingual"] = bool(plan.get("multilingual", False))
        state["web_search"] = bool(plan.get("web_search", True))
        state["graph_retrieval"] = bool(plan.get("graph_retrieval", True))
        state["decompose"] = bool(plan.get("decompose", False))

        return state