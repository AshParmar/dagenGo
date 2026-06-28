from langchain.retrievers.document_compressors import LLMChainExtractor

from llm.models import gemini_llm


class ContextCompressor:

    def __init__(self):

        self.compressor = LLMChainExtractor.from_llm(
            gemini_llm
        )

    def compress(
        self,
        query: str,
        documents,
    ):

        return self.compressor.compress_documents(
            documents=documents,
            query=query,
        )