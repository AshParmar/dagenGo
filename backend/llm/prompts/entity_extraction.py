"""
Entity Extraction prompt — Typed entities for high-quality Knowledge Graph.

Improvements over previous version:
- Added domain-specific entity types: Technique, Tool, Author, Dataset, Language
- Constrained output format with type enum to reduce hallucination
- Shorter system prompt reduces token cost and latency
"""
from langchain_core.prompts import ChatPromptTemplate


entity_extraction_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Extract named entities from text. Return ONLY valid JSON.

Entity types (use exactly): Model, Framework, Paper, Technique, Company, Author, Dataset, Language, Tool, Person, Organization, Country, City, Technology

Format:
{{"entities":[{{"name":"...","type":"..."}}]}}

Rules:
- Only extract entities explicitly mentioned
- Normalize entity names (capitalize properly)
- Skip generic words
- Max {max_entities} entities""",
        ),
        (
            "human",
            "{text}",
        ),
    ]
)