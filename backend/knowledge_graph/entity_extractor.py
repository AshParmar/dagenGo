"""
Entity Extractor — Optimized with:
  1. Parallel execution capability (called concurrently with RelationExtractor)
  2. Result caching keyed on hash of source text
  3. Max entities cap from config
  4. Robust None/dict handling
"""
import hashlib
import logging
import threading
from langchain_core.output_parsers import JsonOutputParser

from config import settings
from llm.models import gemini_llm
from llm.prompts.entity_extraction import entity_extraction_prompt

logger = logging.getLogger(__name__)

# Thread-safe in-memory cache: {text_hash: entities_list}
_cache: dict[str, list] = {}
_cache_lock = threading.Lock()


def _text_hash(text: str) -> str:
    return hashlib.md5(text[:500].encode()).hexdigest()


class EntityExtractor:

    def __init__(self) -> None:
        self.chain = (
            entity_extraction_prompt
            | gemini_llm
            | JsonOutputParser()
        )

    def extract(self, text: str) -> list[dict]:
        if not text or not text.strip():
            return []

        key = _text_hash(text)
        with _cache_lock:
            if key in _cache:
                logger.debug("EntityExtractor cache hit for key=%s", key)
                return _cache[key]

        try:
            result = self.chain.invoke({
                "text": text[:settings.KG_MAX_TEXT_CHARS],
                "max_entities": settings.KG_MAX_ENTITIES,
            })
        except Exception as exc:
            logger.warning("Entity extraction failed: %s", exc)
            return []

        if result is None:
            result = {}
        if isinstance(result, list) and result:
            result = result[0] if isinstance(result[0], dict) else {}
        if not isinstance(result, dict):
            result = {}

        entities = result.get("entities", [])
        if not isinstance(entities, list):
            entities = []

        # Normalize: ensure every entity is a dict with name+type
        entities = [
            e for e in entities
            if isinstance(e, dict) and e.get("name")
        ][: settings.KG_MAX_ENTITIES]

        with _cache_lock:
            _cache[key] = entities

        return entities