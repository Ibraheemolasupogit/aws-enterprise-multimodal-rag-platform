"""Text normalization utilities for local document preprocessing."""

from __future__ import annotations

import re


def count_words(text: str) -> int:
    """Return a simple whitespace-delimited word count."""
    return len(text.split())


def clean_formatting_noise(text: str) -> str:
    """Remove obvious Markdown formatting noise while keeping headings readable."""
    cleaned_lines = []
    for line in text.splitlines():
        stripped = line.strip()

        if stripped.startswith("#"):
            heading_text = stripped.lstrip("#").strip()
            cleaned_lines.append(heading_text)
            continue

        stripped = re.sub(r"`{1,3}", "", stripped)
        stripped = re.sub(r"\*\*(.*?)\*\*", r"\1", stripped)
        stripped = re.sub(r"\*(.*?)\*", r"\1", stripped)
        stripped = re.sub(r"__(.*?)__", r"\1", stripped)
        stripped = re.sub(r"_(.*?)_", r"\1", stripped)
        stripped = re.sub(r"^\s*[-*+]\s+", "", stripped)
        cleaned_lines.append(stripped)

    return "\n".join(cleaned_lines)


def remove_repeated_blank_lines(text: str) -> str:
    """Collapse repeated blank lines to a single paragraph break."""
    return re.sub(r"\n\s*\n+", "\n\n", text)


def normalize_whitespace(text: str) -> str:
    """Normalize spaces and tabs while preserving line boundaries."""
    normalized_lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(normalized_lines).strip()


def preprocess_text(raw_text: str) -> str:
    """Clean local document text without removing useful headings."""
    text = clean_formatting_noise(raw_text)
    text = normalize_whitespace(text)
    text = remove_repeated_blank_lines(text)
    return text.strip()


def preprocess_document(document: dict[str, object]) -> dict[str, object]:
    """Add cleaned text and cleaned counts to a document record."""
    clean_text = preprocess_text(str(document.get("raw_text", "")))
    processed_document = dict(document)
    processed_document.update(
        {
            "clean_text": clean_text,
            "clean_character_count": len(clean_text),
            "clean_word_count": count_words(clean_text),
        }
    )
    return processed_document


def preprocess_documents(documents: list[dict[str, object]]) -> list[dict[str, object]]:
    """Preprocess a list of structured document records."""
    return [preprocess_document(document) for document in documents]
