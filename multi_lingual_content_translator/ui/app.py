"""Streamlit UI for the multi-agent travel content translator."""

import json
import re

import streamlit as st

from multi_lingual_content_translator.config import SUPPORTED_LOCALES, get_settings
from multi_lingual_content_translator.export.formats import (
    export_bundle_i18n,
    export_i18n_json,
    export_xliff,
)
from multi_lingual_content_translator.integrations.brand_rules import (
    TRAVEL_GLOSSARY,
)
from multi_lingual_content_translator.memory.translation_memory import (
    get_translation_memory,
)
from multi_lingual_content_translator.models.schemas import ContentType
from multi_lingual_content_translator.pipeline import (
    translate_content,
    translate_whitelabel_bundle,
)
from multi_lingual_content_translator.samples.sample_hotel_content import (
    SAMPLE_BUNDLE,
    SAMPLE_HOTEL_DESCRIPTION,
    SAMPLE_UI_STRINGS,
)
from multi_lingual_content_translator.ui.theme import (
    THEME_CSS,
    highlight_terms,
    render_booking_preview,
    render_footer,
    render_hero,
    render_stats,
    render_topbar,
)

st.set_page_config(
    page_title="Travel Content Translator",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(THEME_CSS, unsafe_allow_html=True)

TOKEN_PATTERN = re.compile(r"(\{[^}]+\}|%[sd])")


def _locale_label(code: str) -> str:
    return f"{SUPPORTED_LOCALES.get(code, code)} ({code})"


def _render_pipeline_status():
    agents = [
        "Language Detector",
        "Content Segmenter",
        "Glossary Agent",
        "Translation Memory",
        "Translator",
        "QA Reviewer",
    ]
    pills = " ".join(f'<span class="agent-pill">{agent}</span>' for agent in agents)
    st.markdown(
        f'<div class="pipeline-label">Multi-agent pipeline</div>{pills}',
        unsafe_allow_html=True,
    )


def _render_qa_badge(score: float, passed: bool):
    css = "qa-pass" if passed else "qa-fail"
    label = "PASSED" if passed else "NEEDS REVIEW"
    st.markdown(
        f'<span class="{css}">QA {score:.0%} — {label}</span>',
        unsafe_allow_html=True,
    )


def _extract_tokens(text: str) -> list[str]:
    return list(dict.fromkeys(TOKEN_PATTERN.findall(text)))


def _glossary_terms_in_text(text: str) -> list[str]:
    lowered = text.lower()
    return [term for term in TRAVEL_GLOSSARY if term.lower() in lowered]


def _render_side_by_side(source: str, translated: str):
    tokens = _extract_tokens(source)
    glossary = _glossary_terms_in_text(source)

    col_src, col_tgt = st.columns(2)
    with col_src:
        st.markdown('<div class="compare-label">Source</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="compare-panel source">{highlight_terms(source, glossary, tokens)}</div>',
            unsafe_allow_html=True,
        )
    with col_tgt:
        st.markdown('<div class="compare-label">Translation</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="compare-panel target">{highlight_terms(translated, glossary, tokens)}</div>',
            unsafe_allow_html=True,
        )


def _render_export_buttons(result: dict, prefix: str):
    exp_col1, exp_col2, exp_col3 = st.columns(3)
    with exp_col1:
        st.download_button(
            "⬇️ JSON",
            data=json.dumps(result, indent=2, ensure_ascii=False),
            file_name=f"{prefix}_{result['job_id']}.json",
            mime="application/json",
            use_container_width=True,
        )
    with exp_col2:
        st.download_button(
            "⬇️ i18n JSON",
            data=export_i18n_json(result),
            file_name=f"{prefix}_{result['job_id']}_i18n.json",
            mime="application/json",
            use_container_width=True,
        )
    with exp_col3:
        st.download_button(
            "⬇️ XLIFF",
            data=export_xliff(result),
            file_name=f"{prefix}_{result['job_id']}.xliff",
            mime="application/xml",
            use_container_width=True,
        )


def _render_single_result(result: dict):
    st.markdown('<div class="tt-card">', unsafe_allow_html=True)
    st.markdown('<div class="tt-card-title">📋 Translation results</div>', unsafe_allow_html=True)

    meta_col1, meta_col2, meta_col3, meta_col4 = st.columns(4)
    with meta_col1:
        st.metric("Segments", result["segments_count"])
    with meta_col2:
        st.metric("TM hits", result.get("tm_hits", 0))
    with meta_col3:
        st.metric("TM stored", result.get("tm_stored", 0))
    with meta_col4:
        st.metric("Retries", result.get("retry_count", 0))

    st.caption(
        f"Job `{result['job_id']}` · "
        f"**{result['source_locale']}** → {', '.join(result['target_locales'])} · "
        f"Type: **{result['content_type']}**"
    )

    pipeline_errors = [
        err for err in result.get("errors", [])
        if not err.startswith("LLM (")
    ]
    if pipeline_errors:
        st.error("Pipeline errors: " + "; ".join(pipeline_errors))

    source_text = result.get("source_content", "")
    locale_tabs = st.tabs(
        [_locale_label(r["locale"]) for r in result["results"]]
    )
    for tab, locale_result in zip(locale_tabs, result["results"]):
        with tab:
            qa = locale_result.get("qa_report") or {}
            _render_qa_badge(qa.get("score", 0), qa.get("passed", False))

            mode = locale_result.get("metadata", {}).get("translation_mode", "")
            if mode:
                st.caption(f"Engine: {mode}")

            _render_side_by_side(source_text, locale_result["translated_text"])

            if qa.get("issues"):
                st.warning("Issues: " + "; ".join(qa["issues"]))
            if qa.get("suggestions"):
                st.info("Suggestions: " + "; ".join(qa["suggestions"]))
            if qa.get("back_translation"):
                with st.expander("Back-translation check"):
                    st.write(qa["back_translation"])

    _render_export_buttons(result, "translation")
    st.markdown("</div>", unsafe_allow_html=True)


def _render_bundle_result(result: dict):
    st.markdown('<div class="tt-card">', unsafe_allow_html=True)
    st.markdown('<div class="tt-card-title">🏨 Localized hotel bundle</div>', unsafe_allow_html=True)

    st.caption(
        f"Partner **{result['brand_name']}** · "
        f"{result['items_translated']} items translated"
    )

    for locale, items in result["localized_content"].items():
        with st.expander(f"{_locale_label(locale)} — {len(items)} items", expanded=False):
            for key, text in items.items():
                st.markdown(f"**{key}**")
                st.write(text)
                st.divider()

    dl_col1, dl_col2 = st.columns(2)
    with dl_col1:
        st.download_button(
            "⬇️ Bundle JSON",
            data=json.dumps(result, indent=2, ensure_ascii=False),
            file_name=f"bundle_{result['partner_id']}.json",
            mime="application/json",
            use_container_width=True,
        )
    with dl_col2:
        st.download_button(
            "⬇️ i18n JSON",
            data=export_bundle_i18n(result),
            file_name=f"bundle_{result['partner_id']}_i18n.json",
            mime="application/json",
            use_container_width=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def _build_localized_strings(ui_results: dict, locale: str) -> dict[str, str]:
    strings = dict(SAMPLE_UI_STRINGS)
    for key, result in ui_results.items():
        for locale_result in result.get("results", []):
            if locale_result["locale"] == locale:
                strings[key] = locale_result["translated_text"]
    return strings


def main():
    settings = get_settings()
    tm_count = get_translation_memory().count()

    st.markdown(render_topbar(), unsafe_allow_html=True)
    st.markdown(render_hero(), unsafe_allow_html=True)
    st.markdown(render_stats(len(SUPPORTED_LOCALES)), unsafe_allow_html=True)
    _render_pipeline_status()
    st.divider()

    with st.sidebar:
        st.markdown("### ⚙️ Localization settings")
        st.caption("Configure source and target languages for your travel site.")

        source_locale = st.selectbox(
            "Source language",
            options=list(SUPPORTED_LOCALES.keys()),
            format_func=_locale_label,
            index=list(SUPPORTED_LOCALES.keys()).index(settings["default_source_locale"]),
        )

        default_targets = [loc for loc in settings["target_locales"] if loc in SUPPORTED_LOCALES]
        target_locales = st.multiselect(
            "Target languages",
            options=[k for k in SUPPORTED_LOCALES if k != source_locale],
            default=default_targets,
            format_func=_locale_label,
        )

        content_type = st.selectbox(
            "Content type",
            options=[ct.value for ct in ContentType],
            format_func=lambda v: v.replace("_", " ").title(),
            index=0,
        )

        st.divider()
        st.markdown("**Partner**")
        st.caption("TravelAsia Partner")
        st.caption(f"Partner ID: {SAMPLE_BUNDLE.partner_id}")
        st.caption(f"Translation memory: {tm_count} entries")
        st.caption("QA threshold: {:.0%}".format(settings["qa_score_threshold"]))

    tab_single, tab_bundle, tab_ui, tab_preview = st.tabs(
        ["📝 Single content", "🏨 Hotel bundle", "🔤 UI strings", "📱 Live preview"]
    )

    with tab_single:
        st.markdown(
            '<div class="tt-card-title">Hotel & policy content</div>',
            unsafe_allow_html=True,
        )
        st.caption("Paste or load sample hotel description, cancellation policy, or amenity text.")

        if "source_text" not in st.session_state:
            st.session_state["source_text"] = ""

        action_col1, action_col2, _ = st.columns([1, 1, 3])
        with action_col1:
            if st.button("📋 Load sample hotel", use_container_width=True):
                st.session_state["source_text"] = SAMPLE_HOTEL_DESCRIPTION
                st.rerun()
        with action_col2:
            if st.button("Clear", use_container_width=True):
                st.session_state["source_text"] = ""
                st.rerun()

        source_text = st.text_area(
            "Source content",
            height=220,
            placeholder="Paste hotel description, policy text, or UI copy here…",
            key="source_text",
            label_visibility="collapsed",
        )

        if st.button("🌐 Translate now", type="primary", disabled=not source_text.strip()):
            if not target_locales:
                st.warning("Select at least one target language in the sidebar.")
            else:
                with st.spinner("Running multi-agent pipeline…"):
                    result = translate_content(
                        content=source_text,
                        target_locales=target_locales,
                        source_locale=source_locale,
                        content_type=ContentType(content_type),
                    )
                st.session_state["last_single_result"] = result

        if "last_single_result" in st.session_state:
            st.divider()
            _render_single_result(st.session_state["last_single_result"])

    with tab_bundle:
        st.markdown(
            '<div class="tt-card-title">Full content bundle</div>',
            unsafe_allow_html=True,
        )
        st.caption("Translate hotel, rooms, UI strings, and policies in one batch.")

        info_col1, info_col2, info_col3 = st.columns(3)
        with info_col1:
            st.metric("Hotel", SAMPLE_BUNDLE.hotel.name if SAMPLE_BUNDLE.hotel else "—")
        with info_col2:
            st.metric("Rooms", len(SAMPLE_BUNDLE.hotel.rooms) if SAMPLE_BUNDLE.hotel else 0)
        with info_col3:
            st.metric("UI strings", len(SAMPLE_BUNDLE.ui_strings))

        if st.button("🌐 Translate full bundle", type="primary"):
            if not target_locales:
                st.warning("Select at least one target language in the sidebar.")
            else:
                items = SAMPLE_BUNDLE.extract_translatable_items()
                progress = st.progress(0, text=f"Translating 0 / {len(items)} items…")
                status = st.empty()

                def on_progress(current: int, total: int, key: str):
                    progress.progress(current / total, text=f"Translating {current} / {total}…")
                    status.caption(f"Current: `{key}`")

                with st.spinner("Translating hotel, rooms, UI strings, and policies…"):
                    result = translate_whitelabel_bundle(
                        SAMPLE_BUNDLE,
                        target_locales=target_locales,
                        on_progress=on_progress,
                    )
                progress.progress(1.0, text="Done")
                status.caption(f"Completed {result['items_translated']} items.")
                st.session_state["last_bundle_result"] = result

        if "last_bundle_result" in st.session_state:
            st.divider()
            _render_bundle_result(st.session_state["last_bundle_result"])

    with tab_ui:
        st.markdown(
            '<div class="tt-card-title">Booking UI strings</div>',
            unsafe_allow_html=True,
        )
        st.caption("Localize buttons, labels, and prompts on your booking flow.")

        edited_strings = {}
        cols = st.columns(2)
        for idx, (key, value) in enumerate(SAMPLE_UI_STRINGS.items()):
            with cols[idx % 2]:
                edited_strings[key] = st.text_input(
                    key.replace("_", " ").title(),
                    value=value,
                    key=f"ui_{key}",
                )

        if st.button("🌐 Translate UI strings", type="primary"):
            if not target_locales:
                st.warning("Select at least one target language in the sidebar.")
            else:
                ui_results = {}
                progress_bar = st.progress(0)
                items = list(edited_strings.items())
                for i, (key, text) in enumerate(items):
                    progress_bar.progress(
                        (i + 1) / len(items),
                        text=f"Translating {key}…",
                    )
                    ui_results[key] = translate_content(
                        content=text,
                        target_locales=target_locales,
                        source_locale=source_locale,
                        content_type=ContentType.UI_STRING,
                    )
                st.session_state["last_ui_results"] = ui_results

        if "last_ui_results" in st.session_state:
            st.divider()
            for key, result in st.session_state["last_ui_results"].items():
                st.markdown(f"### {key.replace('_', ' ').title()}")
                result_cols = st.columns(len(result["results"]))
                for col, locale_result in zip(result_cols, result["results"]):
                    with col:
                        st.caption(_locale_label(locale_result["locale"]))
                        st.markdown(
                            f'<div class="locale-result">{locale_result["translated_text"]}</div>',
                            unsafe_allow_html=True,
                        )

    with tab_preview:
        st.markdown(
            '<div class="tt-card-title">Mock booking page preview</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "See how translated UI strings and hotel content appear on a booking page."
        )

        if "last_ui_results" not in st.session_state:
            st.info("Translate UI strings first (🔤 UI strings tab), then return here to preview.")
        else:
            preview_locale = st.selectbox(
                "Preview locale",
                options=target_locales or list(SUPPORTED_LOCALES.keys()),
                format_func=_locale_label,
            )
            strings = _build_localized_strings(
                st.session_state["last_ui_results"],
                preview_locale,
            )

            hotel_name = SAMPLE_BUNDLE.hotel.name if SAMPLE_BUNDLE.hotel else "Grand Marina Resort"
            hotel_desc = ""
            if "last_single_result" in st.session_state:
                for r in st.session_state["last_single_result"]["results"]:
                    if r["locale"] == preview_locale:
                        hotel_desc = r["translated_text"]
                        break
            if not hotel_desc:
                hotel_desc = SAMPLE_HOTEL_DESCRIPTION

            st.markdown(
                render_booking_preview(
                    locale=preview_locale,
                    strings=strings,
                    hotel_name=hotel_name,
                    hotel_desc=hotel_desc,
                ),
                unsafe_allow_html=True,
            )

    st.markdown(render_footer(), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
