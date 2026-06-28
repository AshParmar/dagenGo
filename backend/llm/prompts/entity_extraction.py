from langchain_core.prompts import ChatPromptTemplate


entity_extraction_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are DagenGo's Entity Extraction Agent.

Extract every important named entity from the text.

Entity Types:
- Person
- Organization
- Country
- City
- Language
- Dataset
- Model
- Framework
- Research Paper
- Library
- University
- Technology

Return ONLY valid JSON.

Format:

{
    "entities":[
        {
            "name":"...",
            "type":"..."
        }
    ]
}
"""
        ),
        (
            "human",
            """
{text}
"""
        ),
    ]
)