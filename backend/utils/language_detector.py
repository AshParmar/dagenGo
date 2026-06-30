from langdetect import detect, DetectorFactory

# Makes detection deterministic
DetectorFactory.seed = 42


class LanguageDetector:
    """
    Detects the language of a user query.
    """

    def detect_language(self, text: str) -> str:
        """
        Detect the language code (ISO 639-1).

        Example:
            "Hello" -> "en"
            "नमस्ते" -> "hi"
            "こんにちは" -> "ja"
        """
        try:
            return detect(text)
        except Exception:
            return "unknown"


def detect_language(text: str) -> str:
    """Detect language from free text."""
    return LanguageDetector().detect_language(text)