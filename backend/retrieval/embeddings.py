from langchain_community.embeddings import HuggingFaceEmbeddings

from config import settings


embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)