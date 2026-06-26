from langchain_core.prompts import ChatPromptTemplate


rewrite_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are DagenGo's Query Rewrite Agent.

Your job is to improve the user's query for retrieval.

Rules:
1. Preserve the original intent.
2. Remove ambiguity.
3. Expand abbreviations when useful.
4. Keep important named entities unchanged.
5. Do NOT answer the question.
6. Return only the rewritten query.
            """,
        ),
        (
            "human",
            """
Original Query:

{query}

Detected Language:

{language}
            """,
        ),
    ]
)
