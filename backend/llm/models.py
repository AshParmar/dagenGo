from langchain_google_genai import ChatGoogleGenerativeAI

from config import settings


gemini_llm = ChatGoogleGenerativeAI(
    model=settings.GEMINI_MODEL,
    temperature=0.2,
)
