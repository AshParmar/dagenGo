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

def repair_json_unescaped_quotes(text: str) -> str:
    """Repair JSON strings that have unescaped double quotes inside string values."""
    pattern = r'("[a-zA-Z0-9_\-]+"\s*:\s*")'
    matches = list(re.finditer(pattern, text))
    if not matches:
        return text
        
    chunks = []
    last_idx = 0
    for i in range(len(matches)):
        start_match = matches[i]
        key_part = start_match.group(0)
        start_val_idx = start_match.end()
        
        end_search_limit = matches[i+1].start() if i + 1 < len(matches) else len(text)
        
        closing_pattern = r'"\s*(?:,|\n|\]|\})'
        closing_matches = list(re.finditer(closing_pattern, text[start_val_idx:end_search_limit]))
        if closing_matches:
            closing_match = closing_matches[-1]
            end_val_idx = start_val_idx + closing_match.start()
            
            val_content = text[start_val_idx:end_val_idx]
            escaped_val = ""
            escaped = False
            for char in val_content:
                if char == '\\':
                    escaped = not escaped
                    escaped_val += char
                elif char == '"':
                    if not escaped:
                        escaped_val += '\\"'
                    else:
                        escaped_val += char
                    escaped = False
                else:
                    escaped = False
                    escaped_val += char
            
            chunks.append(text[last_idx:start_match.start()])
            chunks.append(key_part)
            chunks.append(escaped_val)
            chunks.append('"')
            last_idx = start_val_idx + closing_match.end() - (closing_match.end() - closing_match.start() - 1)
            
    chunks.append(text[last_idx:])
    return "".join(chunks)

def extract_fallback_values(text: str) -> dict:
    """Extract metrics and decisions from conversational LLM output if JSON parsing fails."""
    data = {}
    
    # Extract approved / supported
    text_lower = text.lower()
    if "approved: true" in text_lower or "supported: true" in text_lower or "is_supported: true" in text_lower or "**supported:** true" in text_lower or "**approved:** true" in text_lower:
        data["approved"] = True
        data["supported"] = True
    elif "approved: false" in text_lower or "supported: false" in text_lower or "is_supported: false" in text_lower or "**supported:** false" in text_lower or "**approved:** false" in text_lower:
        data["approved"] = False
        data["supported"] = False
        
    # Extract action
    for action in ("retrieve_again", "web_search", "graph_retrieve", "ask_user", "continue", "abort"):
        if action in text_lower or action.replace("_", " ") in text_lower:
            data["action"] = action
            break
            
    # Extract query type
    for q_type in ("keyword", "concept", "general", "comparison"):
        if q_type in text_lower:
            data["query_type"] = q_type
            break
            
    # Extract boolean flags
    if "web_search: true" in text_lower or "web search: true" in text_lower or "web_search: yes" in text_lower:
        data["web_search"] = True
    elif "web_search: false" in text_lower or "web search: false" in text_lower or "web_search: no" in text_lower:
        data["web_search"] = False
        
    if "graph_retrieval: true" in text_lower or "graph retrieval: true" in text_lower or "graph_retrieval: yes" in text_lower:
        data["graph_retrieval"] = True
    elif "graph_retrieval: false" in text_lower or "graph retrieval: false" in text_lower or "graph_retrieval: no" in text_lower:
        data["graph_retrieval"] = False
        
    # Extract percentages/numbers using regex
    confidence_match = re.search(r"(?:confidence|confidence score)\s*[:*]*\s*(\d+)%", text, re.IGNORECASE)
    if confidence_match:
        data["confidence_score"] = float(confidence_match.group(1)) / 100.0
        
    groundedness_match = re.search(r"(?:groundedness|groundedness score)\s*[:*]*\s*(\d+)%", text, re.IGNORECASE)
    if groundedness_match:
        data["groundedness_score"] = float(groundedness_match.group(1)) / 100.0
        
    hallucination_match = re.search(r"(?:hallucination|hallucination score)\s*[:*]*\s*(\d+)%", text, re.IGNORECASE)
    if hallucination_match:
        data["hallucination_score"] = float(hallucination_match.group(1)) / 100.0
        
    # Extract improved query / final answer
    improved_query_match = re.search(r"(?:improved query|improved_query)\s*[:*]*\s*(.*)", text, re.IGNORECASE)
    if improved_query_match:
        data["improved_query"] = improved_query_match.group(1).strip('`"\'* ')
        
    final_answer_match = re.search(r"(?:final answer|final_answer)\s*[:*]*\s*(.*)", text, re.IGNORECASE)
    if final_answer_match:
        data["final_answer"] = final_answer_match.group(1).strip('`"\'* ')
        
    return data

def _custom_parse_result(self, result, *, partial: bool = False):
    text = result[0].text
    cleaned = _clean_text_for_json(text)
    
    # Repair unescaped double quotes inside string values before parsing
    cleaned = repair_json_unescaped_quotes(cleaned)
    
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
                return parse_json_markdown(repair_json_unescaped_quotes(text.strip()))
            except JSONDecodeError as orig_e:
                import logging
                logging.getLogger("models").warning(f"Failed to parse JSON from LLM output: {text}. Returning fallback parsed dict.")
                return extract_fallback_values(text)

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
