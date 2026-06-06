# Multilingual Content Translator

Multi-agent travel content localization platform built with LangGraph, Streamlit, and translation memory.

## Quick start

```bash
uv sync
source .venv/bin/activate
cp .env.example .env   # optional: add OPENAI_API_KEY
python main.py ui
```

## CLI

```bash
python main.py demo --locales th,ja,ko
python main.py translate --text "Free cancellation" --locales th,ja
python main.py deck    # open architecture presentation
```
