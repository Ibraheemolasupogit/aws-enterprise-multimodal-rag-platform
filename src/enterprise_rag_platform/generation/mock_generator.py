"""Deterministic local mock RAG generator."""

from __future__ import annotations

import hashlib


GENERATION_MODE = "mock_local_generation"


def build_answer_id(query_id: str, prompt_id: str) -> str:
    """Create a deterministic answer identifier."""
    digest = hashlib.sha256(f"{query_id}|{prompt_id}".encode("utf-8")).hexdigest()[:16]
    return f"answer_{digest}"


def _shorten_text(text: str, max_words: int = 36) -> str:
    words = text.split()
    if len(words) <= max_words:
        return " ".join(words)
    return " ".join(words[:max_words]) + "..."


def generate_mock_answer(prompt: dict[str, object]) -> dict[str, object]:
    """Generate a deterministic, citation-bearing mock answer from context blocks."""
    context_blocks = list(prompt.get("context_blocks", []))
    query_id = str(prompt["query_id"])
    prompt_id = str(prompt["prompt_id"])
    answer_id = build_answer_id(query_id, prompt_id)

    if not context_blocks:
        return {
            "answer_id": answer_id,
            "query_id": query_id,
            "answer_text": (
                "Insufficient evidence: no retrieved context was available to answer "
                "the question."
            ),
            "used_citations": [],
            "generation_mode": GENERATION_MODE,
            "limitations": [
                "This is deterministic local mock generation.",
                "No external model or AWS service was called.",
                "No answer claims were made because no context was provided.",
            ],
        }

    first_block = context_blocks[0]
    citation_label = str(first_block["citation_label"])
    evidence_summary = _shorten_text(str(first_block["text"]))
    answer_text = (
        f"Based on the retrieved policy context, {evidence_summary} "
        f"{citation_label}"
    )

    return {
        "answer_id": answer_id,
        "query_id": query_id,
        "answer_text": answer_text,
        "used_citations": [citation_label],
        "generation_mode": GENERATION_MODE,
        "limitations": [
            "This is deterministic local mock generation.",
            "The response summarizes retrieved text and is not produced by an LLM.",
            "No external model, paid API, or AWS service was called.",
        ],
    }
