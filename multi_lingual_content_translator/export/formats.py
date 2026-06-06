"""Export translated content to standard localization formats."""

import json
import xml.etree.ElementTree as ET
from xml.dom import minidom


def export_i18n_json(result: dict) -> str:
    """React/Vue i18n JSON keyed by locale."""
    source = result.get("source_content", "")
    output: dict[str, dict[str, str]] = {}

    for locale_result in result.get("results", []):
        locale = locale_result["locale"]
        output[locale] = {
            "content": locale_result["translated_text"],
            "_source": source,
            "_qa_score": str(
                (locale_result.get("qa_report") or {}).get("score", "")
            ),
        }

    return json.dumps(output, indent=2, ensure_ascii=False)


def export_bundle_i18n(bundle_result: dict) -> str:
    """Nested i18n JSON for whitelabel bundle content keys."""
    return json.dumps(
        bundle_result.get("localized_content", {}),
        indent=2,
        ensure_ascii=False,
    )


def export_xliff(result: dict) -> str:
    """XLIFF 1.2 export for LSP / CAT tool workflows."""
    xliff = ET.Element(
        "xliff",
        {
            "version": "1.2",
            "xmlns": "urn:oasis:names:tc:xliff:document:1.2",
        },
    )
    file_elem = ET.SubElement(
        xliff,
        "file",
        {
            "source-language": result.get("source_locale", "en"),
            "datatype": "plaintext",
            "original": result.get("job_id", "translation"),
        },
    )
    body = ET.SubElement(file_elem, "body")

    source_segments = result.get("source_segments", [])
    if not source_segments:
        source_segments = [
            {"id": "seg_0", "text": result.get("source_content", "")}
        ]

    for locale_result in result.get("results", []):
        locale = locale_result["locale"]
        target_segments = locale_result.get("segments") or [
            {"id": "seg_0", "text": locale_result["translated_text"]}
        ]
        target_by_id = {s["id"]: s["text"] for s in target_segments}

        for segment in source_segments:
            unit = ET.SubElement(
                body,
                "trans-unit",
                {"id": f"{locale}_{segment['id']}"},
            )
            ET.SubElement(unit, "source").text = segment["text"]
            ET.SubElement(unit, "target", {"language": locale}).text = (
                target_by_id.get(segment["id"], "")
            )

    rough = ET.tostring(xliff, encoding="unicode")
    return minidom.parseString(rough).toprettyxml(indent="  ")
