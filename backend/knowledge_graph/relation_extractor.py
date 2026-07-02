"""
Relation Extractor — Optimized with:
  1. Parallel execution capability (called concurrently with EntityExtractor)
  2. Result caching keyed on hash of (source_text, entities)
  3. Max relations cap from config
  4. Robust None/dict handling
"""
import hashlib
import logging
import threading
from langchain_core.output_parsers import JsonOutputParser

from config import settings
from llm.models import gemini_llm
from llm.prompts.relation_extraction import relation_extraction_prompt

logger = logging.getLogger(__name__)

# Thread-safe in-memory cache: {cache_key: relations_list}
_cache: dict[str, list] = {}
_cache_lock = threading.Lock()


def _cache_key(text: str, entities: list) -> str:
    entity_names = ",".join(sorted(e.get("name", "") for e in entities if isinstance(e, dict)))
    combined = f"{text[:300]}||{entity_names}"
    return hashlib.md5(combined.encode()).hexdigest()


class RelationExtractor:

    def __init__(self) -> None:
        self.chain = (
            relation_extraction_prompt
            | gemini_llm
            | JsonOutputParser()
        )

    def extract(self, text: str, entities: list) -> list[dict]:
        if not text or not text.strip() or not entities:
            return []

        key = _cache_key(text, entities)
        with _cache_lock:
            if key in _cache:
                logger.debug("RelationExtractor cache hit for key=%s", key)
                return _cache[key]

        # Only pass entity names to reduce prompt tokens
        entity_names = [e.get("name") for e in entities if isinstance(e, dict) and e.get("name")]

        try:
            result = self.chain.invoke({
                "text": text[:settings.KG_MAX_TEXT_CHARS],
                "entities": entity_names,
                "max_relations": settings.KG_MAX_RELATIONS,
            })
        except Exception as exc:
            logger.warning("Relation extraction failed: %s", exc)
            return []

        if result is None:
            result = {}
        if isinstance(result, list) and result:
            result = result[0] if isinstance(result[0], dict) else {}
        if not isinstance(result, dict):
            result = {}

        relations = result.get("relations", [])
        if not isinstance(relations, list):
            relations = []

        # Normalize: ensure every relation has source, relation, target
        relations = [
            r for r in relations
            if isinstance(r, dict) and r.get("source") and r.get("target") and r.get("relation")
        ][: settings.KG_MAX_RELATIONS]

        with _cache_lock:
            _cache[key] = relations

        return relations