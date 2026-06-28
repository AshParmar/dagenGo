from langchain_core.prompts import ChatPromptTemplate


relation_extraction_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are DagenGo's Relation Extraction Agent.

Extract relationships between the given entities.

Rules:
- Return ONLY JSON.
- Use concise relation names in UPPER_SNAKE_CASE.
- Do not invent entities.

Output:

{
    "relations":[
        {
            "source":"...",
            "relation":"...",
            "target":"..."
        }
    ]
}
"""
        ),
        (
            "human",
            """
Text:
{text}

Entities:
{entities}
"""
        ),
    ]
)