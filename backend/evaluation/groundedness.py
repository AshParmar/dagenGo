"""
Heuristic-based groundedness evaluator.

Replaces the previous LLM-based approach. Measures how well the answer is
grounded in the evidence using sentence-level overlap scoring.
"""
import re


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z]{3,}", text.lower()))


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"[.!?]+", text) if len(s.strip()) > 20]


class GroundednessEvaluator:

    def evaluate(
        self,
        query: str,
        answer: str,
        evidence: list[dict],
    ) -> dict:
        if not answer or not evidence:
            return {
                "groundedness_score": 0.0,
                "supported_statements": [],
                "unsupported_statements": [],
            }

        evidence_text = " ".join(doc.get("text", "") for doc in evidence)
        evidence_words = _tokenize(evidence_text)

        sentences = _sentences(answer)
        if not sentences:
            return {
                "groundedness_score": 0.5,
                "supported_statements": [],
                "unsupported_statements": [],
            }

        supported, unsupported = [], []
        scores = []

        for sentence in sentences:
            words = _tokenize(sentence)
            if not words:
                continue
            overlap = len(words & evidence_words) / len(words)
            scores.append(overlap)
            if overlap >= 0.4:
                supported.append(sentence[:120])
            else:
                unsupported.append(sentence[:120])

        groundedness_score = round(sum(scores) / len(scores), 3) if scores else 0.0

        return {
            "groundedness_score": groundedness_score,
            "supported_statements": supported[:5],
            "unsupported_statements": unsupported[:5],
        }