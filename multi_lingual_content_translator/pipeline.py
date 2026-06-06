"""Public API for the multilingual translation orchestrator."""

import uuid
from collections.abc import Callable
from typing import Any

from multi_lingual_content_translator.config import get_settings
from multi_lingual_content_translator.integrations.schemas import (
    WhitelabelContentBundle,
)
from multi_lingual_content_translator.memory.translation_memory import (
    get_translation_memory,
)
from multi_lingual_content_translator.models.schemas import (
    ContentType,
    TranslationJob,
    TranslationResult,
)
from multi_lingual_content_translator.orchestrator import run_translation_pipeline


def _store_translations_in_memory(
    source_content: str,
    source_locale: str,
    content_type: str,
    final_state: dict,
    partner_id: str = "",
) -> int:
    """Persist completed translations into translation memory for reuse."""
    tm = get_translation_memory()
    stored = 0
    segments = final_state.get("segments", [])
    source_by_id = {s["id"]: s["text"] for s in segments}

    if not segments:
        for locale, result in final_state.get("final_results", {}).items():
            tm.store(
                source_text=source_content,
                translated_text=result["translated_text"],
                source_locale=source_locale,
                target_locale=locale,
                content_type=content_type,
                partner_id=partner_id,
            )
            stored += 1
        return stored

    for locale, result in final_state.get("final_results", {}).items():
        for segment in result.get("segments", []):
            source_text = source_by_id.get(segment["id"], segment["text"])
            tm.store(
                source_text=source_text,
                translated_text=segment["text"],
                source_locale=source_locale,
                target_locale=locale,
                content_type=content_type,
                partner_id=partner_id,
            )
            stored += 1
    return stored


def translate_content(
    content: str,
    target_locales: list[str] | None = None,
    source_locale: str | None = None,
    content_type: ContentType = ContentType.UNKNOWN,
    brand_id: str = "travel_site",
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Translate travel content into multiple locales using the multi-agent pipeline.

    Returns a dict with job metadata, per-locale results, and QA reports.
    """
    settings = get_settings()
    job = TranslationJob(
        job_id=str(uuid.uuid4())[:12],
        source_content=content,
        source_locale=source_locale or settings["default_source_locale"],
        target_locales=target_locales or settings["target_locales"],
        content_type=content_type,
        brand_id=brand_id,
        context=context or {},
    )

    final_state = run_translation_pipeline(job.to_state())
    partner_id = (context or {}).get("partner_id", "")

    stored = _store_translations_in_memory(
        source_content=content,
        source_locale=final_state.get("detected_locale", job.source_locale),
        content_type=final_state.get("detected_content_type", job.content_type.value),
        final_state=final_state,
        partner_id=partner_id,
    )

    results = []
    for locale, result in final_state.get("final_results", {}).items():
        results.append(
            TranslationResult(
                locale=locale,
                translated_text=result["translated_text"],
                segments=result.get("segments", []),
                qa_report=result.get("qa_report"),
                metadata={
                    "passed": result.get("passed", False),
                    "translation_mode": final_state.get("translation_modes", {}).get(locale),
                },
            ).model_dump()
        )

    return {
        "job_id": job.job_id,
        "source_content": content,
        "source_segments": final_state.get("segments", []),
        "source_locale": final_state.get("detected_locale", job.source_locale),
        "content_type": final_state.get("detected_content_type", job.content_type.value),
        "target_locales": job.target_locales,
        "segments_count": len(final_state.get("segments", [])),
        "translation_mode": final_state.get("context", {}).get("translation_mode", "unknown"),
        "translation_modes": final_state.get("translation_modes", {}),
        "tm_hits": final_state.get("context", {}).get("tm_hits", 0),
        "tm_stored": stored,
        "retry_count": final_state.get("retry_count", 0),
        "results": results,
        "qa_summary": {
            locale: {
                "score": report.get("score", 0),
                "passed": report.get("passed", False),
                "issues": report.get("issues", []),
            }
            for locale, report in final_state.get("qa_reports", {}).items()
        },
        "errors": final_state.get("errors", []),
        "pipeline_steps": final_state.get("current_step", "unknown"),
    }


def translate_whitelabel_bundle(
    bundle: WhitelabelContentBundle,
    target_locales: list[str] | None = None,
    on_progress: Callable[[int, int, str], None] | None = None,
) -> dict[str, Any]:
    """Translate all items in a travel site content bundle."""
    items = bundle.extract_translatable_items()
    bundle_results: dict[str, dict[str, str]] = {
        locale: {} for locale in (target_locales or get_settings()["target_locales"])
    }

    item_results = []
    total = len(items)
    for idx, item in enumerate(items):
        if on_progress:
            on_progress(idx + 1, total, item["key"])
        result = translate_content(
            content=item["text"],
            target_locales=target_locales,
            source_locale=bundle.locale,
            content_type=item["content_type"],
            context={"key": item["key"], "partner_id": bundle.partner_id},
        )
        result["progress"] = {"current": idx + 1, "total": total, "key": item["key"]}
        item_results.append({"key": item["key"], **result})
        for locale_result in result["results"]:
            bundle_results[locale_result["locale"]][item["key"]] = locale_result[
                "translated_text"
            ]

    return {
        "partner_id": bundle.partner_id,
        "brand_name": bundle.brand_name,
        "source_locale": bundle.locale,
        "items_translated": len(items),
        "localized_content": bundle_results,
        "item_results": item_results,
    }
