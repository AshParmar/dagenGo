from langchain_core.output_parsers import JsonOutputParser

from llm.models import gemini_llm
from llm.prompts.entity_extraction import entity_extraction_prompt


class EntityExtractor:

    def __init__(self):

        self.chain = (
            entity_extraction_prompt
            | gemini_llm
            | JsonOutputParser()
        )

    def extract(self, text: str):

        result = self.chain.invoke(
            {
                "text": text,
            }
        )

        return result["entities"]