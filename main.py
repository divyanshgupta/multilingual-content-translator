"""CLI entrypoint for the multi-agent multilingual content translator."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from multi_lingual_content_translator.agents.base import get_llm_status, has_llm
from multi_lingual_content_translator.config import SUPPORTED_LOCALES, get_settings
from multi_lingual_content_translator.models.schemas import ContentType
from multi_lingual_content_translator.pipeline import (
    translate_content,
    translate_whitelabel_bundle,
)
from multi_lingual_content_translator.samples.sample_hotel_content import (
    SAMPLE_BUNDLE,
    SAMPLE_HOTEL_DESCRIPTION,
)


def _parse_locales(value: str) -> list[str]:
    return [locale.strip() for locale in value.split(",") if locale.strip()]


def cmd_translate(args: argparse.Namespace) -> int:
    content = args.text
    if args.file:
        with open(args.file, encoding="utf-8") as handle:
            content = handle.read()

    if not content:
        print("Error: provide --text or --file with content to translate.", file=sys.stderr)
        return 1

    content_type = ContentType(args.content_type) if args.content_type else ContentType.UNKNOWN
    result = translate_content(
        content=content,
        target_locales=_parse_locales(args.locales) if args.locales else None,
        source_locale=args.source,
        content_type=content_type,
    )

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, ensure_ascii=False)
        print(f"Results written to {args.output}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))

    return 0 if not result.get("errors") else 1


def cmd_demo(args: argparse.Namespace) -> int:
    print("Running demo translation with sample whitelabel hotel content...\n")
    llm_info = get_llm_status()
    print(f"Translation engine: {llm_info['mode']}")
    print(f"{llm_info['message']}\n")

    locales = _parse_locales(args.locales) if args.locales else ["th", "ja", "ko"]
    result = translate_content(
        content=SAMPLE_HOTEL_DESCRIPTION,
        target_locales=locales,
        content_type=ContentType.HOTEL_DESCRIPTION,
    )

    print(f"Job ID: {result['job_id']}")
    print(f"Detected locale: {result['source_locale']}")
    print(f"Content type: {result['content_type']}")
    print(f"Segments: {result['segments_count']}\n")

    for locale_result in result["results"]:
        print(f"--- {locale_result['locale']} ---")
        print(locale_result["translated_text"][:500])
        qa = locale_result.get("qa_report", {})
        print(f"QA score: {qa.get('score', 'N/A')} | Passed: {qa.get('passed', False)}\n")

    return 0


def cmd_bundle(args: argparse.Namespace) -> int:
    locales = _parse_locales(args.locales) if args.locales else None
    result = translate_whitelabel_bundle(SAMPLE_BUNDLE, target_locales=locales)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, ensure_ascii=False)
        print(f"Bundle results written to {args.output}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))

    return 0


def cmd_locales(_: argparse.Namespace) -> int:
    for code, name in sorted(SUPPORTED_LOCALES.items()):
        print(f"  {code:6} {name}")
    return 0


def cmd_presentation(_: argparse.Namespace) -> int:
    deck = Path(__file__).parent / "multi_lingual_content_translator" / "ui" / "presentation.html"
    print(f"Opening architecture deck: {deck}")
    return subprocess.call(["open", str(deck)])


def cmd_ui(args: argparse.Namespace) -> int:
    app_path = Path(__file__).parent / "multi_lingual_content_translator" / "ui" / "app.py"
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
    ]
    if args.port:
        cmd.extend(["--server.port", str(args.port)])
    print("Starting translator UI at http://localhost:8501")
    return subprocess.call(cmd)


def build_parser() -> argparse.ArgumentParser:
    settings = get_settings()
    locale_help = f"Comma-separated locales (default: {','.join(settings['target_locales'])})"

    parser = argparse.ArgumentParser(
        description="Multi-agent multilingual translator for travel whitelabel sites",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    translate_parser = subparsers.add_parser("translate", help="Translate content to multiple locales")
    translate_parser.add_argument("--text", "-t", help="Text content to translate")
    translate_parser.add_argument("--file", "-f", help="File path with content to translate")
    translate_parser.add_argument("--locales", "-l", help=locale_help)
    translate_parser.add_argument("--source", "-s", default=settings["default_source_locale"])
    translate_parser.add_argument(
        "--content-type",
        "-c",
        choices=[ct.value for ct in ContentType],
        help="Content type hint for agents",
    )
    translate_parser.add_argument("--output", "-o", help="Write JSON results to file")
    translate_parser.set_defaults(func=cmd_translate)

    demo_parser = subparsers.add_parser("demo", help="Run demo with sample hotel content")
    demo_parser.add_argument("--locales", "-l", default="th,ja,ko", help=locale_help)
    demo_parser.set_defaults(func=cmd_demo)

    bundle_parser = subparsers.add_parser(
        "bundle",
        help="Translate full whitelabel content bundle (hotel + UI + policies)",
    )
    bundle_parser.add_argument("--locales", "-l", help=locale_help)
    bundle_parser.add_argument("--output", "-o", help="Write JSON results to file")
    bundle_parser.set_defaults(func=cmd_bundle)

    locales_parser = subparsers.add_parser("locales", help="List supported locales")
    locales_parser.set_defaults(func=cmd_locales)

    deck_parser = subparsers.add_parser("deck", help="Open 3-slide architecture HTML presentation")
    deck_parser.set_defaults(func=cmd_presentation)

    ui_parser = subparsers.add_parser("ui", help="Launch the web UI")
    ui_parser.add_argument("--port", "-p", type=int, default=8501, help="Server port")
    ui_parser.set_defaults(func=cmd_ui)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
