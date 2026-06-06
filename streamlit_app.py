"""Streamlit Cloud / Render entrypoint for production deployment."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from multi_lingual_content_translator.ui.app import main

main()
