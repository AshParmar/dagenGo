from langchain_google_genai import GoogleGenerativeAIEmbeddings

from config import settings


embeddings = GoogleGenerativeAIEmbeddings(
    model=settings.EMBEDDING_MODEL
)