"""Query validation and normalization for local retrieval orchestration."""

from __future__ import annotations

import hashlib
import re


def normalize_query(raw_query: str) -> str:
    """Normalize user query whitespace."""
    return re.sub(r"\s+", " ", raw_query).strip()


def build_query_id(normalized_query: str) -> str:
    """Create a deterministic query identifier."""
    digest = hashlib.sha256(normalized_query.encode("utf-8")).hexdigest()[:16]
    return f"query_{digest}"


def process_query(raw_query: str, minimum_query_words: int = 2) -> dict[str, object]:
    """Validate and structure a raw user query."""
    normalized_query = normalize_query(raw_query)
    if not normalized_query:
        raise ValueError("Query must not be empty")

    word_count = len(normalized_query.split())
    if word_count < minimum_query_words:
        raise ValueError(
            f"Query must contain at least {minimum_query_words} words"
        )

    return {
        "query_id": build_query_id(normalized_query),
        "raw_query": raw_query,
        "normalized_query": normalized_query,
        "character_count": len(normalized_query),
        "word_count": word_count,
    }
