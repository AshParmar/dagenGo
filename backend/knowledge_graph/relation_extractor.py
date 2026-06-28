from langchain_core.output_parsers import JsonOutputParser

from llm.models import gemini_llm
from llm.prompts.relation_extraction import relation_extraction_prompt


class RelationExtractor:

    def __init__(self):

        self.chain = (
            relation_extraction_prompt
            | gemini_llm
            | JsonOutputParser()
        )

    def extract(
        self,
        text: str,
        entities: list,
    ):

        result = self.chain.invoke(
            {
                "text": text,
                "entities": entities,
            }
        )

        return result["relations"]