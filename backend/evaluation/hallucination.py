"""
Heuristic-based hallucination detector.

Replaces the previous LLM-based approach which was slow and unreliable with
local models (Llama 3 would return conversational text instead of JSON).

Strategy: measure word-level overlap between the answer and the evidence.
Claims that use words not found in the evidence at all are flagged.
"""
import re


def _tokenize(text: str) -> set[str]:
    """Lowercase word tokens, stripping punctuation."""
    return set(re.findall(r"[a-z]{3,}", text.lower()))


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"[.!?]+", text) if len(s.strip()) > 20]


class HallucinationDetector:

    def evaluate(
        self,
        query: str,
        answer: str,
        evidence: list[dict],
    ) -> dict:
        if not answer or not evidence:
            return {
                "hallucination_score": 0.5,
                "supported_claims": [],
                "partial_claims": [],
                "unsupported_claims": [],
                "hallucinated": False,
            }

        evidence_text = " ".join(doc.get("text", "") for doc in evidence)
        evidence_words = _tokenize(evidence_text)
        answer_words = _tokenize(answer)

        if not answer_words:
            return {
                "hallucination_score": 0.0,
                "supported_claims": [],
                "partial_claims": [],
                "unsupported_claims": [],
                "hallucinated": False,
            }

        # Word-level overlap ratio
        overlap = len(answer_words & evidence_words) / len(answer_words)
        hallucination_score = round(max(0.0, 1.0 - overlap), 3)

        # Sentence-level classification
        supported, partial, unsupported = [], [], []
        for sentence in _sentences(answer):
            sentence_words = _tokenize(sentence)
            if not sentence_words:
                continue
            sent_overlap = len(sentence_words & evidence_words) / len(sentence_words)
            if sent_overlap >= 0.6:
                supported.append(sentence[:120])
            elif sent_overlap >= 0.3:
                partial.append(sentence[:120])
            else:
                unsupported.append(sentence[:120])

        return {
            "hallucination_score": hallucination_score,
            "supported_claims": supported[:5],
            "partial_claims": partial[:5],
            "unsupported_claims": unsupported[:5],
            "hallucinated": hallucination_score > 0.6,
        }