"""
Heuristic-based confidence scorer.

Replaces the previous LLM-based approach. Combines signals from retrieval,
verification, and hallucination analysis without any LLM calls.
"""


class ConfidenceScorer:

    def evaluate(
        self,
        query: str,
        answer: str,
        evidence: list[dict],
        verification: dict,
        hallucination: dict,
    ) -> dict:
        score = 0.0
        reasons = []

        # Signal 1: evidence quantity (max 0.30)
        evidence_count = len(evidence)
        evidence_signal = min(evidence_count / 5.0, 1.0) * 0.30
        score += evidence_signal
        reasons.append(f"{evidence_count} evidence chunks retrieved")

        # Signal 2: verification passed (0.35)
        if verification.get("supported", False):
            score += 0.35
            reasons.append("answer is fully supported by evidence")
        elif not verification.get("needs_reretrieval", True):
            score += 0.15
            reasons.append("answer is partially supported")

        # Signal 3: low hallucination risk (0.25)
        hallucination_score = hallucination.get("hallucination_score", 0.5)
        hallucination_signal = (1.0 - hallucination_score) * 0.25
        score += hallucination_signal
        if hallucination_score < 0.3:
            reasons.append("low hallucination risk")
        elif hallucination_score > 0.6:
            reasons.append("high hallucination risk detected")

        # Signal 4: answer is non-empty (0.10)
        if answer and len(answer.strip()) > 50:
            score += 0.10
            reasons.append("answer is substantive")

        confidence_score = round(min(score, 1.0), 3)

        return {
            "confidence_score": confidence_score,
            "reason": "; ".join(reasons),
        }