"""Agent: Retrieve translation memory matches for segments."""

from multi_lingual_content_translator.memory.translation_memory import (
    get_translation_memory,
)


def retrieve_memory(state: dict) -> dict:
    segments = state.get("segments", [])
    target_locales = state.get("target_locales", [])
    source_locale = state.get("detected_locale") or state.get("source_locale", "en")

    tm = get_translation_memory()
    tm_matches: dict[str, list[dict]] = {}
    tm_hits = 0

    for locale in target_locales:
        locale_matches = []
        for segment in segments:
            matches = tm.search(
                source_text=segment["text"],
                source_locale=source_locale,
                target_locale=locale,
            )
            if matches:
                tm_hits += 1
                locale_matches.append(
                    {
                        "segment_id": segment["id"],
                        "source_text": segment["text"],
                        "matches": matches,
                        "best_match": matches[0],
                    }
                )
        tm_matches[locale] = locale_matches

    return {
        "tm_matches": tm_matches,
        "context": {
            **state.get("context", {}),
            "tm_hits": tm_hits,
            "tm_total": tm.count(),
        },
        "current_step": "memory_retrieved",
    }
