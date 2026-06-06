import json
import re

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from multi_lingual_content_translator.config import get_settings, is_valid_api_key


def get_llm(temperature: float = 0.2) -> ChatOpenAI | None:
    settings = get_settings()
    if not is_valid_api_key(settings["openai_api_key"]):
        return None
    return ChatOpenAI(
        model=settings["openai_model"],
        api_key=settings["openai_api_key"],
        temperature=temperature,
    )


def get_llm_status() -> dict:
    settings = get_settings()
    key = settings["openai_api_key"]
    if not key:
        return {
            "mode": "fallback",
            "message": "No OPENAI_API_KEY set — using Google Translate fallback.",
        }
    if not is_valid_api_key(key):
        return {
            "mode": "fallback",
            "message": "OPENAI_API_KEY is a placeholder — using Google Translate fallback. "
            "Add a real key to .env for LLM-powered translation.",
        }
    return {
        "mode": "llm",
        "message": f"OpenAI {settings['openai_model']} connected.",
    }


def invoke_json(llm: ChatOpenAI, system: str, user: str) -> dict:
    response = llm.invoke(
        [SystemMessage(content=system), HumanMessage(content=user)]
    )
    content = response.content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\n?", "", content)
        content = re.sub(r"\n?```$", "", content)
    return json.loads(content)


def has_llm() -> bool:
    return get_llm() is not None
