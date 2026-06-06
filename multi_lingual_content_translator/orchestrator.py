"""
LangGraph multi-agent orchestrator for multilingual travel content translation.

Pipeline:
  START → Language Detector → Content Segmenter → Glossary Agent → Memory Agent
        → Translator ⇄ QA Reviewer (retry loop) → END
"""

from typing import Any, Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from multi_lingual_content_translator.agents.content_segmenter import segment_content
from multi_lingual_content_translator.agents.glossary_agent import enrich_glossary
from multi_lingual_content_translator.agents.language_detector import (
    detect_language_and_type,
)
from multi_lingual_content_translator.agents.memory_agent import retrieve_memory
from multi_lingual_content_translator.agents.qa_reviewer import review_translation
from multi_lingual_content_translator.agents.translator import translate_segments
from multi_lingual_content_translator.config import get_settings


class TranslationState(TypedDict, total=False):
    job_id: str
    source_content: str
    source_locale: str
    target_locales: list[str]
    content_type: str
    brand_id: str
    context: dict[str, Any]
    detected_locale: str
    detected_content_type: str
    segments: list[dict]
    glossary: dict[str, dict[str, str]]
    tm_matches: dict[str, list[dict]]
    translations: dict[str, list[dict]]
    translation_modes: dict[str, str]
    qa_reports: dict[str, dict]
    qa_feedback: dict[str, dict]
    final_results: dict[str, dict]
    errors: list[str]
    current_step: str
    retry_count: int


def _wrap_agent(agent_fn, agent_name: str):
    def node(state: TranslationState) -> dict:
        try:
            return agent_fn(state)
        except Exception as exc:
            errors = list(state.get("errors", []))
            errors.append(f"{agent_name}: {exc}")
            return {"errors": errors, "current_step": f"{agent_name}_failed"}
    return node


def _prepare_retry(state: TranslationState) -> dict:
    feedback: dict[str, dict] = {}
    for locale, report in state.get("qa_reports", {}).items():
        if not report.get("passed", False):
            feedback[locale] = {
                "issues": report.get("issues", []),
                "suggestions": report.get("suggestions", []),
                "back_translation": report.get("back_translation", ""),
            }
    return {
        "qa_feedback": feedback,
        "retry_count": state.get("retry_count", 0) + 1,
        "current_step": "retrying",
    }


def _route_after_qa(state: TranslationState) -> Literal["retry", "done"]:
    settings = get_settings()
    retries = state.get("retry_count", 0)
    if retries >= settings["max_retries"]:
        return "done"

    threshold = settings["qa_score_threshold"]
    for report in state.get("qa_reports", {}).values():
        if report.get("score", 0) < threshold or not report.get("passed", False):
            return "retry"
    return "done"


def build_translation_graph():
    graph = StateGraph(TranslationState)

    graph.add_node("language_detector", _wrap_agent(detect_language_and_type, "language_detector"))
    graph.add_node("content_segmenter", _wrap_agent(segment_content, "content_segmenter"))
    graph.add_node("glossary_agent", _wrap_agent(enrich_glossary, "glossary_agent"))
    graph.add_node("memory_agent", _wrap_agent(retrieve_memory, "memory_agent"))
    graph.add_node("translator", _wrap_agent(translate_segments, "translator"))
    graph.add_node("qa_reviewer", _wrap_agent(review_translation, "qa_reviewer"))
    graph.add_node("prepare_retry", _prepare_retry)

    graph.add_edge(START, "language_detector")
    graph.add_edge("language_detector", "content_segmenter")
    graph.add_edge("content_segmenter", "glossary_agent")
    graph.add_edge("glossary_agent", "memory_agent")
    graph.add_edge("memory_agent", "translator")
    graph.add_edge("translator", "qa_reviewer")
    graph.add_conditional_edges(
        "qa_reviewer",
        _route_after_qa,
        {"retry": "prepare_retry", "done": END},
    )
    graph.add_edge("prepare_retry", "translator")

    return graph.compile()


_compiled_graph = None


def get_orchestrator():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_translation_graph()
    return _compiled_graph


def run_translation_pipeline(initial_state: dict) -> dict:
    initial_state.setdefault("retry_count", 0)
    orchestrator = get_orchestrator()
    return orchestrator.invoke(initial_state)
