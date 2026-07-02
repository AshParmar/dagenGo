"""
Relation Extraction prompt — Typed, semantically rich relations for Knowledge Graph.

Improvements over previous version:
- Constrained relation vocabulary: avoids generic "RELATED_TO" where possible
- Explicit preferred relation list guides the LLM toward meaningful edges
- Max relations parameter controls output size
"""
from langchain_core.prompts import ChatPromptTemplate


relation_extraction_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Extract relationships between the given entities from the text. Return ONLY valid JSON.

Preferred relation types (use these when applicable):
USES, IMPLEMENTS, SUPPORTS, COMPARES_WITH, BUILT_BY, PART_OF, TRAINED_ON, PUBLISHED_BY, DEVELOPED_BY, AUTHORED_BY, EVALUATED_ON, BASED_ON, RELATED_TO

Rules:
- ONLY use entities from the provided list as source/target
- Use RELATED_TO only as last resort
- Return max {max_relations} relations
- Return empty list if no clear relations exist

Format:
{{"relations":[{{"source":"...","relation":"...","target":"..."}}]}}""",
        ),
        (
            "human",
            """Text:
{text}

Entities:
{entities}""",
        ),
    ]
)