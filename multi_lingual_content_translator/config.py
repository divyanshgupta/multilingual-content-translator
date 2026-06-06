import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()

PLACEHOLDER_API_KEYS = {
    "",
    "sk-your-key-here",
    "your-api-key-here",
    "changeme",
}


def is_valid_api_key(key: str) -> bool:
    if not key or key.strip() in PLACEHOLDER_API_KEYS:
        return False
    if key.startswith("sk-your") or key.startswith("sk-..."):
        return False
    return True


SUPPORTED_LOCALES = {
    "en": "English",
    "th": "Thai",
    "ja": "Japanese",
    "ko": "Korean",
    "zh-CN": "Simplified Chinese",
    "zh-TW": "Traditional Chinese",
    "vi": "Vietnamese",
    "id": "Indonesian",
    "ms": "Malay",
    "ar": "Arabic",
    "hi": "Hindi",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "pt": "Portuguese",
    "ru": "Russian",
}


@lru_cache
def get_settings() -> dict:
    target_locales = os.getenv(
        "TARGET_LOCALES", "th,ja,ko,zh-CN,vi,id,ms"
    ).split(",")
    return {
        "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
        "openai_model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "default_source_locale": os.getenv("DEFAULT_SOURCE_LOCALE", "en"),
        "target_locales": [locale.strip() for locale in target_locales if locale.strip()],
        "qa_score_threshold": float(os.getenv("QA_SCORE_THRESHOLD", "0.75")),
        "max_retries": int(os.getenv("MAX_RETRIES", "2")),
    }
