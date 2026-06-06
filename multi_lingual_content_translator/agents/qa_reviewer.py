"""Agent 5: Quality assurance via back-translation and brand compliance checks."""

from multi_lingual_content_translator.agents.base import get_llm, invoke_json
from multi_lingual_content_translator.config import get_settings


def _heuristic_qa(
    source_segments: list[dict],
    translated_segments: list[dict],
    locale: str,
) -> dict:
    source_text = " ".join(s["text"] for s in source_segments)
    translated_text = " ".join(s["text"] for s in translated_segments)
    length_ratio = len(translated_text) / max(len(source_text), 1)
    score = 0.7 if 0.3 <= length_ratio <= 3.0 else 0.4
    threshold = get_settings()["qa_score_threshold"]

    return {
        "locale": locale,
        "score": score,
        "passed": score >= threshold,
        "issues": [] if score >= threshold else ["Length ratio outside expected range"],
        "back_translation": f"[mock back-translation of {locale} content]",
        "suggestions": [],
    }


def _review_locale(
    source_segments: list[dict],
    translated_segments: list[dict],
    locale: str,
    source_locale: str,
    brand_rules: dict,
) -> dict:
    llm = get_llm(temperature=0.0)
    if llm is None:
        return _heuristic_qa(source_segments, translated_segments, locale)

    source_text = "\n".join(s["text"] for s in source_segments)
    translated_text = "\n".join(s["text"] for s in translated_segments)
    threshold = get_settings()["qa_score_threshold"]

    system = (
        "You are a translation QA reviewer for travel site travel content. "
        "Evaluate translation quality: accuracy, tone, glossary consistency, "
        "and preservation of placeholders/brand names. "
        "Perform mental back-translation to verify meaning. "
        "Return JSON: {\"score\": 0.0-1.0, \"passed\": bool, \"issues\": [], "
        "\"back_translation\": \"...\", \"suggestions\": []}."
    )
    user = (
        f"Source ({source_locale}):\n{source_text}\n\n"
        f"Translation ({locale}):\n{translated_text}\n\n"
        f"Brand rules: {brand_rules}\n"
        f"Pass threshold: {threshold}"
    )

    try:
        result = invoke_json(llm, system, user)
        result["locale"] = locale
        result["passed"] = result.get("score", 0) >= threshold
        return result
    except Exception:
        return _heuristic_qa(source_segments, translated_segments, locale)


def review_translation(state: dict) -> dict:
    segments = state.get("segments", [])
    translations = state.get("translations", {})
    source_locale = state.get("detected_locale") or state.get("source_locale", "en")
    brand_rules = state.get("context", {}).get("brand_rules", {})

    qa_reports: dict[str, dict] = {}
    final_results: dict[str, dict] = {}

    for locale, translated_segments in translations.items():
        qa_report = _review_locale(
            source_segments=segments,
            translated_segments=translated_segments,
            locale=locale,
            source_locale=source_locale,
            brand_rules=brand_rules,
        )
        qa_reports[locale] = qa_report

        translated_text = "\n\n".join(s["text"] for s in translated_segments)
        final_results[locale] = {
            "locale": locale,
            "translated_text": translated_text,
            "segments": translated_segments,
            "qa_report": qa_report,
            "passed": qa_report.get("passed", False),
        }

    return {
        "qa_reports": qa_reports,
        "final_results": final_results,
        "current_step": "qa_complete",
    }
