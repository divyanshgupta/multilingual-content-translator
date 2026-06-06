"""Agent 3: Build locale-specific glossary from travel terms."""

from multi_lingual_content_translator.agents.base import get_llm, invoke_json
from multi_lingual_content_translator.integrations.brand_rules import (
    TRAVEL_GLOSSARY,
    get_brand_rules,
    get_glossary_for_locale,    
    get_locale_guidelines,
)


def _find_relevant_terms(segments: list[dict]) -> set[str]:
    combined = " ".join(segment["text"] for segment in segments).lower()
    return {
        term
        for term in TRAVEL_GLOSSARY
        if term.lower() in combined
    }


def enrich_glossary(state: dict) -> dict:
    segments = state.get("segments", [])
    target_locales = state.get("target_locales", [])
    brand_rules = get_brand_rules()

    glossary: dict[str, dict[str, str]] = {}
    relevant_terms = _find_relevant_terms(segments)

    for locale in target_locales:
        locale_glossary = get_glossary_for_locale(locale)
        glossary[locale] = {
            term: locale_glossary[term]
            for term in relevant_terms
            if term in locale_glossary
        }
        glossary[locale]["__guidelines__"] = get_locale_guidelines(locale)

    llm = get_llm(temperature=0.1)
    if llm is not None and segments:
        combined_text = " ".join(s["text"] for s in segments)[:2000]
        system = (
            "You are a travel industry terminology expert for travel sites. "
            "Given source text, suggest additional domain-specific terms that need "
            "consistent translation. Return JSON: "
            "{\"additional_terms\": {\"term\": {\"locale\": \"translation\"}}}."
        )
        user = (
            f"Target locales: {', '.join(target_locales)}\n"
            f"Brand rules: {brand_rules['tone']}\n"
            f"Source text: {combined_text}"
        )
        try:
            result = invoke_json(llm, system, user)
            for term, locale_map in result.get("additional_terms", {}).items():
                for locale, translation in locale_map.items():
                    if locale in glossary:
                        glossary[locale][term] = translation
        except Exception:
            pass

    return {
        "glossary": glossary,
        "current_step": "glossary_ready",
        "context": {
            **state.get("context", {}),
            "brand_rules": brand_rules,
        },
    }
