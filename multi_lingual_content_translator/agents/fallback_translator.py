"""Fallback translator using Google Translate when LLM is unavailable."""

import re

from multi_lingual_content_translator.integrations.brand_rules import (
    TRAVEL_GLOSSARY,
)

LOCALE_MAP = {
    "zh-CN": "zh-CN",
    "zh-TW": "zh-TW",
}

TOKEN_PATTERN = re.compile(
    r"(\{[^}]+\}|%[sd]|<[^>]+>|https?://\S+)"
)


def _map_locale(locale: str) -> str:
    return LOCALE_MAP.get(locale, locale.split("-")[0])


def _apply_glossary(text: str, locale: str) -> str:
    result = text
    for term, translations in TRAVEL_GLOSSARY.items():
        if locale in translations:
            result = re.sub(
                re.escape(term),
                translations[locale],
                result,
                flags=re.IGNORECASE,
            )
    return result


def _translate_text(text: str, source_locale: str, target_locale: str) -> str:
    from deep_translator import GoogleTranslator

    translator = GoogleTranslator(
        source=_map_locale(source_locale),
        target=_map_locale(target_locale),
    )
    return translator.translate(text)


def _translate_preserving_tokens(
    text: str,
    source_locale: str,
    target_locale: str,
) -> str:
    tokens = TOKEN_PATTERN.findall(text)
    if not tokens:
        translated = _translate_text(text, source_locale, target_locale)
        return _apply_glossary(translated, target_locale)

    placeholder_map: dict[str, str] = {}
    masked = text
    for idx, token in enumerate(tokens):
        key = f"__TOKEN_{idx}__"
        placeholder_map[key] = token
        masked = masked.replace(token, key, 1)

    translated = _translate_text(masked, source_locale, target_locale)
    for key, token in placeholder_map.items():
        translated = translated.replace(key, token)

    return _apply_glossary(translated, target_locale)


def translate_segments_fallback(
    segments: list[dict],
    source_locale: str,
    target_locale: str,
) -> list[dict]:
    translated_segments = []
    for segment in segments:
        translated_segments.append(
            {
                **segment,
                "text": _translate_preserving_tokens(
                    segment["text"],
                    source_locale,
                    target_locale,
                ),
            }
        )
    return translated_segments
