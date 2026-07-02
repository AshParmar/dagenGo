"""
Verifier Agent — Optimized with:
  1. Heuristic fast-path: Skip LLM call when confidence is already very high
  2. Reduced evidence window: 3 chunks max (was 5) to cut prompt tokens
  3. Reduced answer window: 2000 chars (was 4000) to cut prompt tokens
  4. Minimal prompt to reduce LLM thinking time
"""
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from config import settings
from graph.state import DagenGoState
from llm.models import gemini_llm

logger = logging.getLogger(__name__)

verifier_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Verify if the answer is supported by the evidence. Return ONLY JSON.
{{"supported":true,"supported_claims":[],"unsupported_claims":[],"missing_information":[],"needs_reretrieval":false}}""",
        ),
        (
            "human",
            """Query: {query}

Evidence (top 3):
{evidence}

Answer (first 2000 chars):
{answer}""",
        ),
    ]
)


class VerifierAgent:

    def __init__(self) -> None:
        self.chain = (
            verifier_prompt
            | gemini_llm
            | JsonOutputParser()
        )

    def _heuristic_verify(self, state: DagenGoState) -> dict | None:
        """
        Fast heuristic verification — returns a result dict if we can determine
        the answer quality without calling the LLM.

        Returns None if LLM verification is required.
        """
        answer = state.get("answer", "")
        evidence = state.get("reranked_results", [])
        confidence_score = state.get("confidence", {}).get("confidence_score", 0.0)

        # If answer is empty, flag as unsupported immediately
        if not answer or len(answer.strip()) < 20:
            return {
                "supported": False,
                "supported_claims": [],
                "unsupported_claims": ["Answer is empty or too short"],
                "missing_information": ["Full answer needed"],
                "needs_reretrieval": True,
            }

        # If no evidence, flag as needing retrieval
        if not evidence:
            return {
                "supported": False,
                "supported_claims": [],
                "unsupported_claims": [],
                "missing_information": ["No evidence retrieved"],
                "needs_reretrieval": True,
            }

        # Skip LLM when confidence is already very high
        if confidence_score >= settings.SKIP_VERIFICATION_CONFIDENCE_THRESHOLD:
            logger.debug(
                "Skipping LLM verification (confidence=%.2f >= threshold=%.2f)",
                confidence_score,
                settings.SKIP_VERIFICATION_CONFIDENCE_THRESHOLD,
            )
            return {
                "supported": True,
                "supported_claims": [],
                "unsupported_claims": [],
                "missing_information": [],
                "needs_reretrieval": False,
            }

        return None  # Need LLM call

    def invoke(self, state: DagenGoState) -> DagenGoState:
        # Fast heuristic path first
        heuristic_result = self._heuristic_verify(state)
        if heuristic_result is not None:
            verification = heuristic_result
        else:
            try:
                # Truncate inputs to reduce prompt size
                evidence_text = [
                    {"title": d.get("title", ""), "text": d.get("text", "")[:500]}
                    for d in state.get("reranked_results", [])[:3]
                ]
                verification = self.chain.invoke(
                    {
                        "query": state["query"],
                        "evidence": evidence_text,
                        "answer": state.get("answer", "")[:2000],
                    }
                )
            except Exception as exc:
                logger.warning("Verifier LLM call failed: %s — using defaults", exc)
                verification = {}

        if isinstance(verification, list) and verification:
            verification = verification[0]
        if not isinstance(verification, dict):
            verification = {}

        state["verification"] = verification
        state["supported"] = bool(verification.get("supported", False))
        state["needs_reretrieval"] = bool(verification.get("needs_reretrieval", False))

        return state