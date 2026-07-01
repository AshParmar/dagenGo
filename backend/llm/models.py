from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama
import re
from json import JSONDecodeError
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.utils.json import parse_json_markdown

# Monkey-patch JsonOutputParser to be robust against conversational text before/after JSON
# when running local models (like Llama 3) via Ollama.
def _clean_text_for_json(text: str) -> str:
    # Try finding markdown code block: ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # Try finding the first '{' and matching it to the last '}'
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and start < end:
        return text[start:end+1].strip()
        
    return text.strip()

def _custom_parse_result(self, result, *, partial: bool = False):
    text = result[0].text
    cleaned = _clean_text_for_json(text)
    
    if partial:
        try:
            return parse_json_markdown(cleaned)
        except JSONDecodeError:
            return None
    else:
        try:
            return parse_json_markdown(cleaned)
        except JSONDecodeError as e:
            try:
                # Fallback to the original implementation
                return parse_json_markdown(text.strip())
            except JSONDecodeError as orig_e:
                import logging
                logging.getLogger("models").warning(f"Failed to parse JSON from LLM output: {text}. Returning empty dict.")
                return {}

JsonOutputParser.parse_result = _custom_parse_result

import contextvars
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.messages import AIMessage
from config import settings

# Global ContextVar to store user settings for the current query request
request_settings = contextvars.ContextVar("request_settings", default={})

def get_dynamic_model():
    run_settings = request_settings.get() or {}
    provider = str(run_settings.get("provider", "gemini")).lower()
    model_name = run_settings.get("model")
    temperature = float(run_settings.get("temperature", 0.3))

    if provider == "gemini" and settings.GOOGLE_API_KEY:
        return ChatGoogleGenerativeAI(
            model=model_name or settings.GEMINI_MODEL,
            temperature=temperature,
        )
    elif provider == "claude" and settings.ANTHROPIC_API_KEY:
        try:
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=model_name or settings.CLAUDE_MODEL,
                temperature=temperature,
            )
        except Exception:
            pass
    elif provider == "gpt" and settings.OPENAI_API_KEY:
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=model_name or settings.OPENAI_MODEL,
                temperature=temperature,
            )
        except Exception:
            pass

    # Default fallback: local Ollama Llama 3
    return ChatOllama(
        model="llama3",
        temperature=temperature,
    )

class DynamicChatModel(BaseChatModel):
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        return get_dynamic_model()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)

    @property
    def _llm_type(self) -> str:
        return "dynamic_chat_model"

    def invoke(self, input, config=None, **kwargs):
        return get_dynamic_model().invoke(input, config=config, **kwargs)

    async def ainvoke(self, input, config=None, **kwargs):
        return await get_dynamic_model().ainvoke(input, config=config, **kwargs)

    def stream(self, input, config=None, **kwargs):
        return get_dynamic_model().stream(input, config=config, **kwargs)

    async def astream(self, input, config=None, **kwargs):
        async for chunk in get_dynamic_model().astream(input, config=config, **kwargs):
            yield chunk

gemini_llm = DynamicChatModel()
