"""Local document loading utilities for sample enterprise documents."""

from __future__ import annotations

from pathlib import Path


SUPPORTED_EXTENSIONS = {".md", ".txt"}


def count_words(text: str) -> int:
    """Return a simple whitespace-delimited word count."""
    return len(text.split())


def build_document_id(source_file: Path) -> str:
    """Create a stable local document identifier from a source filename."""
    return source_file.stem.lower().replace(" ", "_")


def load_document(source_file: Path) -> dict[str, object]:
    """Load one supported local document into a structured record."""
    raw_text = source_file.read_text(encoding="utf-8")

    return {
        "document_id": build_document_id(source_file),
        "source_file": source_file.name,
        "raw_text": raw_text,
        "character_count": len(raw_text),
        "word_count": count_words(raw_text),
    }


def load_documents(input_document_dir: str | Path) -> list[dict[str, object]]:
    """Load Markdown and plain-text documents from a local directory."""
    document_dir = Path(input_document_dir)
    if not document_dir.exists():
        raise FileNotFoundError(f"Input document directory does not exist: {document_dir}")

    documents = []
    for source_file in sorted(document_dir.iterdir()):
        if source_file.is_file() and source_file.suffix.lower() in SUPPORTED_EXTENSIONS:
            documents.append(load_document(source_file))

    return documents
