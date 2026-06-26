from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from config import settings


gemini_llm = ChatGoogleGenerativeAI(
    model=settings.GEMINI_MODEL,
    temperature=0.2,
)

openai_llm = ChatOpenAI(
    model=settings.OPENAI_MODEL,
    temperature=0.2,
)

claude_llm = ChatAnthropic(
    model=settings.CLAUDE_MODEL,
    temperature=0.2,
)