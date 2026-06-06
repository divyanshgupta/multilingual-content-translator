"""Agent 1: Detect source language and content type."""

from multi_lingual_content_translator.agents.base import get_llm, invoke_json
from multi_lingual_content_translator.models.schemas import ContentType


def _heuristic_detect(content: str, hinted_locale: str, hinted_type: str) -> dict:
    detected_locale = hinted_locale or "en"
    detected_type = hinted_type or ContentType.UNKNOWN.value

    lowered = content.lower()
    type_signals = {
        ContentType.CANCELLATION_POLICY.value: ["cancel", "refund", "non-refundable"],
        ContentType.BOOKING_POLICY.value: ["check-in", "check-out", "booking"],
        ContentType.UI_STRING.value: ["book now", "search", "select dates"],
        ContentType.ROOM_DESCRIPTION.value: ["room", "bed", "sqm", "sq ft"],
        ContentType.HOTEL_DESCRIPTION.value: ["hotel", "located", "amenities"],
    }
    for content_type, keywords in type_signals.items():
        if any(keyword in lowered for keyword in keywords):
            detected_type = content_type
            break

    return {
        "detected_locale": detected_locale,
        "detected_content_type": detected_type,
        "confidence": 0.6,
        "reasoning": "Heuristic detection (no API key configured).",
    }


def detect_language_and_type(state: dict) -> dict:
    content = state["source_content"]
    hinted_locale = state.get("source_locale", "en")
    hinted_type = state.get("content_type", ContentType.UNKNOWN.value)

    llm = get_llm(temperature=0.0)
    if llm is None:
        result = _heuristic_detect(content, hinted_locale, hinted_type)
    else:
        system = (
            "You are a language and content classifier for a travel booking website. "
            "Return JSON with keys: detected_locale (ISO code), detected_content_type "
            "(one of: hotel_description, room_description, amenity_list, booking_policy, "
            "cancellation_policy, ui_string, payment_terms, search_result, email_template, unknown), "
            "confidence (0-1), reasoning."
        )
        user = f"Classify this content:\n\n{content[:3000]}"
        try:
            result = invoke_json(llm, system, user)
        except Exception as exc:
            result = _heuristic_detect(content, hinted_locale, hinted_type)
            result["reasoning"] = f"LLM failed ({exc}); used heuristics."

    return {
        "detected_locale": result.get("detected_locale", hinted_locale),
        "detected_content_type": result.get(
            "detected_content_type", hinted_type
        ),
        "current_step": "language_detected",
        "context": {
            **state.get("context", {}),
            "detection": result,
        },
    }
