"""Agent 2: Segment content into translatable chunks while preserving tokens."""

import re
import uuid

from multi_lingual_content_translator.agents.base import get_llm, invoke_json
from multi_lingual_content_translator.models.schemas import ContentType


TOKEN_PATTERN = re.compile(
    r"(\{[^}]+\}|%[sd]|<[^>]+>|https?://\S+|\b[A-Z]{3}\b)"
)


def _extract_preserve_tokens(text: str) -> list[str]:
    return list(dict.fromkeys(TOKEN_PATTERN.findall(text)))


def _heuristic_segment(content: str, content_type: str) -> list[dict]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", content) if p.strip()]
    if not paragraphs:
        paragraphs = [content]

    segments = []
    for paragraph in paragraphs:
        segments.append(
            {
                "id": str(uuid.uuid4())[:8],
                "text": paragraph,
                "content_type": content_type,
                "preserve_tokens": _extract_preserve_tokens(paragraph),
            }
        )
    return segments


def segment_content(state: dict) -> dict:
    content = state["source_content"]
    content_type = state.get("detected_content_type") or state.get(
        "content_type", ContentType.UNKNOWN.value
    )

    llm = get_llm(temperature=0.0)
    if llm is None:
        segments = _heuristic_segment(content, content_type)
    else:
        system = (
            "You segment travel website content for translation. "
            "Split into logical segments (paragraphs, UI strings, or policy clauses). "
            "Return JSON: {\"segments\": [{\"id\": \"seg_1\", \"text\": \"...\", "
            "\"content_type\": \"...\", \"preserve_tokens\": [\"{price}\"]}]}. "
            "Never split inside HTML tags, placeholders, or URLs."
        )
        user = f"Content type: {content_type}\n\nContent:\n{content[:4000]}"
        try:
            result = invoke_json(llm, system, user)
            segments = result.get("segments", [])
            if not segments:
                segments = _heuristic_segment(content, content_type)
        except Exception:
            segments = _heuristic_segment(content, content_type)

    for segment in segments:
        if "preserve_tokens" not in segment:
            segment["preserve_tokens"] = _extract_preserve_tokens(segment["text"])

    return {
        "segments": segments,
        "current_step": "segmented",
    }
