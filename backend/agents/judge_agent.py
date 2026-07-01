from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from graph.state import DagenGoState
from llm.models import gemini_llm


judge_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are DagenGo's Final Judge.

Review the entire pipeline.

Evaluate:

1. Is the answer correct?
2. Is every important claim supported?
3. Is confidence high?
4. Is hallucination risk acceptable?

Return ONLY JSON.

IMPORTANT: The `final_answer` field MUST be written entirely in {language}. Do not translate or change to any other language.

{{
    "approved": true,
    "reason": "",
    "final_answer": ""
}}
"""
        ),
        (
            "human",
            """
Query:
{query}

Answer:
{answer}

Evidence:
{evidence}

Verification:
{verification}

Evaluation Metrics:
- Confidence Score: {confidence_score}
- Groundedness Score: {groundedness_score}
- Hallucination Score: {hallucination_score}
"""
        ),
    ]
)


class JudgeAgent:

    def __init__(self):

        self.chain = (
            judge_prompt
            | gemini_llm
            | JsonOutputParser()
        )

    def invoke(
        self,
        state: DagenGoState,
    ) -> DagenGoState:

        # Use the auto-detected language from the language_node stage
        language = state.get("language") or "English"

        result = self.chain.invoke(
            {
                "query": state["query"],
                "answer": state["answer"],
                "evidence": state["reranked_results"],
                "verification": state["verification"],
                "confidence_score": f"{state.get('confidence', {}).get('confidence_score', 0.0) * 100:.0f}%",
                "groundedness_score": f"{state.get('groundedness', {}).get('groundedness_score', 0.0) * 100:.0f}%",
                "hallucination_score": f"{state.get('hallucination', {}).get('hallucination_score', 0.0) * 100:.0f}%",
                "language": language,
            }
        )

        if isinstance(result, list) and len(result) > 0:
            result = result[0]

        if not isinstance(result, dict):
            result = {}

        state["approved"] = bool(result.get("approved", False))

        state["judge_reason"] = result.get("reason", "")

        final_ans = result.get("final_answer")
        if not final_ans or not final_ans.strip():
            final_ans = state.get("answer", "")
        state["final_answer"] = final_ans

        # Programmatic Guardrails: Reject if hallucination score is too high or groundedness is too low
        # only if we haven't exhausted our retry budget (limit of 2 retries)
        current_retry = int(state.get("retry_count", 0))
        if current_retry < 2:
            confidence = state.get("confidence", {}).get("confidence_score", 0.0)
            groundedness = state.get("groundedness", {}).get("groundedness_score", 0.0)
            hallucination = state.get("hallucination", {}).get("hallucination_score", 0.0)

            # Strict cutoff thresholds: Reject if hallucination > 40% or groundedness < 30%
            if hallucination > 0.4:
                state["approved"] = False
                state["judge_reason"] = f"Rejected by quality guardrails: Hallucination risk ({hallucination*100:.1f}%) exceeds the 40.0% limit."
            elif groundedness < 0.3:
                state["approved"] = False
                state["judge_reason"] = f"Rejected by quality guardrails: Groundedness score ({groundedness*100:.1f}%) is below the 30.0% requirement."

        if not state["approved"]:
            state["retry_count"] = state.get("retry_count", 0) + 1

        return state