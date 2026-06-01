"""Simple local word-based document chunking."""

from __future__ import annotations


def chunk_text(clean_text: str, chunk_size_words: int, chunk_overlap_words: int) -> list[str]:
    """Split text into overlapping word chunks."""
    if chunk_size_words <= 0:
        raise ValueError("chunk_size_words must be greater than zero")
    if chunk_overlap_words < 0:
        raise ValueError("chunk_overlap_words cannot be negative")
    if chunk_overlap_words >= chunk_size_words:
        raise ValueError("chunk_overlap_words must be smaller than chunk_size_words")

    words = clean_text.split()
    if not words:
        return []

    chunks = []
    step = chunk_size_words - chunk_overlap_words
    for start in range(0, len(words), step):
        chunk_words = words[start : start + chunk_size_words]
        if not chunk_words:
            continue
        chunks.append(" ".join(chunk_words))
        if start + chunk_size_words >= len(words):
            break

    return chunks


def chunk_document(
    document: dict[str, object],
    chunk_size_words: int,
    chunk_overlap_words: int,
) -> list[dict[str, object]]:
    """Create structured chunks for one preprocessed document."""
    document_id = str(document["document_id"])
    source_file = str(document["source_file"])
    clean_text = str(document.get("clean_text", ""))
    text_chunks = chunk_text(clean_text, chunk_size_words, chunk_overlap_words)

    return [
        {
            "document_id": document_id,
            "source_file": source_file,
            "chunk_id": f"{document_id}_chunk_{chunk_index:04d}",
            "chunk_index": chunk_index,
            "text": text,
            "word_count": len(text.split()),
        }
        for chunk_index, text in enumerate(text_chunks)
        if text.strip()
    ]


def chunk_documents(
    documents: list[dict[str, object]],
    chunk_size_words: int,
    chunk_overlap_words: int,
) -> list[dict[str, object]]:
    """Create chunks for a list of preprocessed documents."""
    chunks = []
    for document in documents:
        chunks.extend(chunk_document(document, chunk_size_words, chunk_overlap_words))
    return chunks
