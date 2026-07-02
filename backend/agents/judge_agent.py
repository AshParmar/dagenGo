"""
Judge Agent — Optimized with:
  1. Reduced evidence window: 3 chunks max (was all reranked)
  2. Reduced answer window: 3000 chars (was unlimited)
  3. Programmatic quality guardrails unchanged (hallucination/groundedness thresholds)
  4. More direct prompt to reduce LLM thinking time
  5. Evidence passed as compact text (not full dicts) to reduce token count
"""
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from graph.state import DagenGoState
from llm.models import gemini_llm

logger = logging.getLogger(__name__)

judge_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are DagenGo's Final Quality Judge.

Approve the answer if it is accurate, well-supported, and complete.
Reject ONLY if there are clear factual errors or the answer ignores the query.

Return ONLY JSON:
{{"approved":true,"reason":""}}""",
        ),
        (
            "human",
            """Query: {query}

Answer:
{answer}

Evidence (top 3 chunks):
{evidence}

Scores: Confidence={confidence_score}, Groundedness={groundedness_score}, Hallucination={hallucination_score}
Verification: supported={supported}""",
        ),
    ]
)


class JudgeAgent:

    def __init__(self) -> None:
        self.chain = (
            judge_prompt
            | gemini_llm
            | JsonOutputParser()
        )

    def invoke(self, state: DagenGoState) -> DagenGoState:
        language = state.get("language") or "English"

        # Build compact evidence text instead of sending full dicts
        evidence_chunks = state.get("reranked_results", [])[:3]
        evidence_text = "\n\n".join(
            f"[{d.get('title', 'Source')}] {d.get('text', '')[:400]}"
            for d in evidence_chunks
        )

        try:
            result = self.chain.invoke(
                {
                    "query": state["query"],
                    "answer": state.get("answer", "")[:3000],
                    "evidence": evidence_text,
                    "confidence_score": f"{state.get('confidence', {}).get('confidence_score', 0.0) * 100:.0f}%",
                    "groundedness_score": f"{state.get('groundedness', {}).get('groundedness_score', 0.0) * 100:.0f}%",
                    "hallucination_score": f"{state.get('hallucination', {}).get('hallucination_score', 0.0) * 100:.0f}%",
                    "supported": str(state.get("supported", False)),
                }
            )
        except Exception as exc:
            logger.warning("Judge LLM call failed: %s — defaulting to approved", exc)
            result = {}

        if isinstance(result, list) and result:
            result = result[0]
        if not isinstance(result, dict):
            result = {}

        state["approved"] = bool(result.get("approved", False))
        state["judge_reason"] = result.get("reason", "")
        state["final_answer"] = state.get("answer", "")

        # Programmatic guardrails (unchanged from original logic)
        current_retry = int(state.get("retry_count", 0))
        if current_retry < 2:
            confidence = state.get("confidence", {}).get("confidence_score", 0.0)
            groundedness = state.get("groundedness", {}).get("groundedness_score", 0.0)
            hallucination = state.get("hallucination", {}).get("hallucination_score", 0.0)

            if hallucination > 0.4:
                state["approved"] = False
                state["judge_reason"] = (
                    f"Rejected by quality guardrails: Hallucination risk "
                    f"({hallucination * 100:.1f}%) exceeds the 40.0% limit."
                )
            elif groundedness < 0.3:
                state["approved"] = False
                state["judge_reason"] = (
                    f"Rejected by quality guardrails: Groundedness score "
                    f"({groundedness * 100:.1f}%) is below the 30.0% requirement."
                )

        if not state["approved"]:
            state["retry_count"] = state.get("retry_count", 0) + 1

        return state