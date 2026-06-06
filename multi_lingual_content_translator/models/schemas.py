from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ContentType(str, Enum):
    HOTEL_DESCRIPTION = "hotel_description"
    ROOM_DESCRIPTION = "room_description"
    AMENITY_LIST = "amenity_list"
    BOOKING_POLICY = "booking_policy"
    CANCELLATION_POLICY = "cancellation_policy"
    UI_STRING = "ui_string"
    PAYMENT_TERMS = "payment_terms"
    SEARCH_RESULT = "search_result"
    EMAIL_TEMPLATE = "email_template"
    UNKNOWN = "unknown"


class ContentSegment(BaseModel):
    id: str
    text: str
    content_type: ContentType = ContentType.UNKNOWN
    preserve_tokens: list[str] = Field(default_factory=list)


class QAReport(BaseModel):
    locale: str
    score: float = Field(ge=0.0, le=1.0)
    passed: bool
    issues: list[str] = Field(default_factory=list)
    back_translation: str = ""
    suggestions: list[str] = Field(default_factory=list)


class TranslationResult(BaseModel):
    locale: str
    translated_text: str
    segments: list[ContentSegment] = Field(default_factory=list)
    qa_report: QAReport | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class TranslationJob(BaseModel):
    job_id: str
    source_content: str
    source_locale: str = "en"
    target_locales: list[str]
    content_type: ContentType = ContentType.UNKNOWN
    brand_id: str = "travel_site"
    context: dict[str, Any] = Field(default_factory=dict)

    def to_state(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "source_content": self.source_content,
            "source_locale": self.source_locale,
            "target_locales": self.target_locales,
            "content_type": self.content_type.value,
            "brand_id": self.brand_id,
            "context": self.context,
            "detected_locale": "",
            "detected_content_type": "",
            "segments": [],
            "glossary": {},
            "tm_matches": {},
            "translations": {},
            "translation_modes": {},
            "qa_reports": {},
            "qa_feedback": {},
            "final_results": {},
            "errors": [],
            "retry_count": 0,
            "current_step": "init",
        }
