"""Translation memory with exact-match store and optional semantic search."""

import hashlib
import json
import os
from difflib import SequenceMatcher
from functools import lru_cache

SIMILARITY_THRESHOLD = 0.88
EXACT_MATCH_THRESHOLD = 0.96


class TranslationMemory:
    def __init__(self, persist_dir: str | None = None):
        self.persist_dir = persist_dir or os.getenv(
            "TM_PERSIST_DIR",
            os.path.join(os.getcwd(), ".translation_memory"),
        )
        os.makedirs(self.persist_dir, exist_ok=True)
        self.index_path = os.path.join(self.persist_dir, "index.json")
        self._index: dict[str, dict] = self._load_index()
        self._semantic = None
        self._init_semantic()

    def _load_index(self) -> dict[str, dict]:
        if os.path.exists(self.index_path):
            with open(self.index_path, encoding="utf-8") as handle:
                return json.load(handle)
        return {}

    def _save_index(self) -> None:
        with open(self.index_path, "w", encoding="utf-8") as handle:
            json.dump(self._index, handle, ensure_ascii=False, indent=2)

    def _init_semantic(self) -> None:
        try:
            cache_dir = os.path.join(self.persist_dir, "hf_cache")
            os.makedirs(cache_dir, exist_ok=True)
            os.environ.setdefault("HF_HOME", cache_dir)
            os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", cache_dir)

            import chromadb
            from chromadb.utils import embedding_functions

            ef = embedding_functions.DefaultEmbeddingFunction()
            client = chromadb.PersistentClient(
                path=os.path.join(self.persist_dir, "chroma"),
            )
            self._semantic = client.get_or_create_collection(
                name="translation_memory",
                embedding_function=ef,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception:
            self._semantic = None

    def _entry_key(
        self,
        source_text: str,
        source_locale: str,
        target_locale: str,
    ) -> str:
        raw = f"{source_locale}|{target_locale}|{source_text.strip()}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def store(
        self,
        source_text: str,
        translated_text: str,
        source_locale: str,
        target_locale: str,
        content_type: str = "unknown",
        partner_id: str = "",
    ) -> None:
        if not source_text.strip() or not translated_text.strip():
            return

        key = self._entry_key(source_text, source_locale, target_locale)
        entry = {
            "source_text": source_text.strip(),
            "translated_text": translated_text.strip(),
            "source_locale": source_locale,
            "target_locale": target_locale,
            "content_type": content_type,
            "partner_id": partner_id,
        }
        self._index[key] = entry
        self._save_index()

        if self._semantic is not None:
            try:
                self._semantic.upsert(
                    ids=[key],
                    documents=[source_text.strip()],
                    metadatas=[entry],
                )
            except Exception:
                pass

    def _fuzzy_matches(
        self,
        source_text: str,
        source_locale: str,
        target_locale: str,
        n_results: int,
    ) -> list[dict]:
        matches = []
        for key, entry in self._index.items():
            if entry["source_locale"] != source_locale:
                continue
            if entry["target_locale"] != target_locale:
                continue
            ratio = SequenceMatcher(
                None,
                source_text.strip().lower(),
                entry["source_text"].lower(),
            ).ratio()
            if ratio < SIMILARITY_THRESHOLD:
                continue
            matches.append(
                {
                    "id": key,
                    "source_text": entry["source_text"],
                    "translated_text": entry["translated_text"],
                    "similarity": round(ratio, 4),
                    "exact_match": ratio >= EXACT_MATCH_THRESHOLD,
                    "content_type": entry.get("content_type", ""),
                }
            )
        matches.sort(key=lambda m: m["similarity"], reverse=True)
        return matches[:n_results]

    def search(
        self,
        source_text: str,
        source_locale: str,
        target_locale: str,
        n_results: int = 3,
    ) -> list[dict]:
        if not source_text.strip():
            return []

        key = self._entry_key(source_text, source_locale, target_locale)
        if key in self._index:
            entry = self._index[key]
            return [
                {
                    "id": key,
                    "source_text": entry["source_text"],
                    "translated_text": entry["translated_text"],
                    "similarity": 1.0,
                    "exact_match": True,
                    "content_type": entry.get("content_type", ""),
                }
            ]

        if self._semantic is not None and self._semantic.count() > 0:
            try:
                results = self._semantic.query(
                    query_texts=[source_text.strip()],
                    n_results=min(n_results, self._semantic.count()),
                    where={"target_locale": target_locale, "source_locale": source_locale},
                )
                matches = []
                for doc_id, distance, document, metadata in zip(
                    results["ids"][0],
                    results["distances"][0],
                    results["documents"][0],
                    results["metadatas"][0],
                ):
                    similarity = 1 - distance
                    if similarity < SIMILARITY_THRESHOLD:
                        continue
                    matches.append(
                        {
                            "id": doc_id,
                            "source_text": document,
                            "translated_text": metadata.get("translated_text", ""),
                            "similarity": round(similarity, 4),
                            "exact_match": similarity >= EXACT_MATCH_THRESHOLD,
                            "content_type": metadata.get("content_type", ""),
                        }
                    )
                if matches:
                    return matches
            except Exception:
                pass

        return self._fuzzy_matches(source_text, source_locale, target_locale, n_results)

    def count(self) -> int:
        return len(self._index)


@lru_cache
def get_translation_memory() -> TranslationMemory:
    return TranslationMemory()
