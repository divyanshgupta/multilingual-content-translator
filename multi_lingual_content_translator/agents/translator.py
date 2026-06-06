"""Agent 4: Translate segments into target locales."""

import json

from multi_lingual_content_translator.agents.base import get_llm, invoke_json
from multi_lingual_content_translator.agents.fallback_translator import (
    translate_segments_fallback,
)
from multi_lingual_content_translator.config import SUPPORTED_LOCALES
from multi_lingual_content_translator.integrations.brand_rules import (
    get_brand_rules,
)


def _apply_tm_matches(
    segments: list[dict],
    tm_matches: list[dict],
) -> tuple[list[dict], list[dict]]:
    """Return segments still needing translation and those resolved from TM."""
    match_by_id = {
        m["segment_id"]: m["best_match"]
        for m in tm_matches
        if m["best_match"].get("exact_match")
    }

    resolved = []
    remaining = []
    for segment in segments:
        hit = match_by_id.get(segment["id"])
        if hit:
            resolved.append({**segment, "text": hit["translated_text"], "from_tm": True})
        else:
            remaining.append(segment)
    return remaining, resolved


def _translate_with_llm(
    segments: list[dict],
    locale: str,
    source_locale: str,
    glossary: dict[str, str],
    content_type: str,
    tm_matches: list[dict],
    qa_feedback: dict | None = None,
) -> list[dict]:
    llm = get_llm(temperature=0.3)
    if llm is None:
        raise RuntimeError("LLM not configured")

    locale_name = SUPPORTED_LOCALES.get(locale, locale)
    source_name = SUPPORTED_LOCALES.get(source_locale, source_locale)
    brand_rules = get_brand_rules()
    guidelines = glossary.pop("__guidelines__", "")

    glossary_text = json.dumps(
        {k: v for k, v in glossary.items() if not k.startswith("__")},
        ensure_ascii=False,
    )
    tm_context = json.dumps(
        [
            {
                "source": m["source_text"],
                "translation": m["best_match"]["translated_text"],
                "similarity": m["best_match"]["similarity"],
            }
            for m in tm_matches
        ],
        ensure_ascii=False,
    )
    segments_payload = json.dumps(segments, ensure_ascii=False)
    feedback_text = json.dumps(qa_feedback or {}, ensure_ascii=False)

    system = (
        f"You are an expert translator for travel sites. "
        f"Translate from {source_name} ({source_locale}) to {locale_name} ({locale}). "
        f"Content type: {content_type}. "   
        f"Brand tone: {brand_rules['tone']}. "
        f"Locale guidelines: {guidelines}. "
        f"Preserve exactly: {', '.join(brand_rules['preserve'])}. "
        f"Use glossary terms consistently: {glossary_text}. "
        f"Translation memory hints (reuse when appropriate): {tm_context}. "
        f"QA feedback to address: {feedback_text}. "
        "Return JSON: {\"segments\": [{\"id\": \"...\", \"text\": \"translated\", "
        "\"content_type\": \"...\", \"preserve_tokens\": [...]}]}."
    )
    user = f"Translate these segments:\n{segments_payload}"

    result = invoke_json(llm, system, user)
    translated = result.get("segments", [])
    if not translated:
        raise RuntimeError("LLM returned empty segments")
    return translated


def _translate_for_locale(
    segments: list[dict],
    locale: str,
    source_locale: str,
    glossary: dict[str, str],
    content_type: str,
    tm_matches: list[dict],
    qa_feedback: dict | None = None,
) -> tuple[list[dict], str, list[str]]:
    errors: list[str] = []
    remaining, from_tm = _apply_tm_matches(segments, tm_matches)

    if not remaining:
        return from_tm, "translation_memory", errors

    translated: list[dict] = []
    mode = "fallback"

    try:
        translated = _translate_with_llm(
            segments=remaining,
            locale=locale,
            source_locale=source_locale,
            glossary=dict(glossary),
            content_type=content_type,
            tm_matches=tm_matches,
            qa_feedback=qa_feedback,
        )
        mode = "llm"
    except Exception as exc:
        errors.append(f"LLM ({locale}): {exc}")
        try:
            translated = translate_segments_fallback(remaining, source_locale, locale)
            mode = "fallback"
        except Exception as fallback_exc:
            errors.append(f"Fallback ({locale}): {fallback_exc}")
            raise RuntimeError(f"All translation methods failed for {locale}") from fallback_exc

    return from_tm + translated, mode, errors


def translate_segments(state: dict) -> dict:
    segments = state.get("segments", [])
    target_locales = state.get("target_locales", [])
    source_locale = state.get("detected_locale") or state.get("source_locale", "en")
    content_type = state.get("detected_content_type") or state.get("content_type", "unknown")
    glossary = state.get("glossary", {})
    tm_matches = state.get("tm_matches", {})
    qa_feedback = state.get("qa_feedback", {})

    translations: dict[str, list[dict]] = {}
    translation_modes: dict[str, str] = {}
    errors = list(state.get("errors", []))

    for locale in target_locales:
        locale_glossary = dict(glossary.get(locale, {}))
        translated, mode, locale_errors = _translate_for_locale(
            segments=segments,
            locale=locale,
            source_locale=source_locale,
            glossary=locale_glossary,
            content_type=content_type,
            tm_matches=tm_matches.get(locale, []),
            qa_feedback=qa_feedback.get(locale),
        )
        translations[locale] = translated
        translation_modes[locale] = mode
        errors.extend(locale_errors)

    modes = set(translation_modes.values())
    if modes == {"translation_memory"}:
        overall_mode = "translation_memory"
    elif "llm" in modes:
        overall_mode = "llm"
    else:
        overall_mode = "fallback"

    return {
        "translations": translations,
        "translation_modes": translation_modes,
        "context": {
            **state.get("context", {}),
            "translation_mode": overall_mode,
        },
        "errors": errors,
        "current_step": "translated",
    }
