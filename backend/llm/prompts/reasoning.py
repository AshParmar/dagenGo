from langchain_core.prompts import ChatPromptTemplate


reasoning_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are Veritas AI.

Answer ONLY from the provided context.

If insufficient evidence exists, say so.

Always cite the document used.
"""
        ),
        (
            "human",
            """
Question:

{query}

Context:

{context}
"""
        )
    ]
)