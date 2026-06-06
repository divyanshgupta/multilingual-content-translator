# Multilingual Content Translator

Multi-agent travel content localization platform built with LangGraph, Streamlit, and translation memory.

## Production

| Service | URL |
|---------|-----|
| **Landing page** | https://divyanshgupta.github.io/multilingual-content-translator/ |
| **Architecture deck** | https://divyanshgupta.github.io/multilingual-content-translator/presentation.html |
| **Live app** | Deploy on [Streamlit Cloud](https://share.streamlit.io) → main file: `streamlit_app.py` |

## Quick start (local)

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
