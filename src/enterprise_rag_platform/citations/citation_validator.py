"""Citation validation for local mock RAG answers."""

from __future__ import annotations


def validate_citations(
    answer: dict[str, object],
    contexts: list[dict[str, object]],
) -> dict[str, object]:
    """Validate that answer citations are supported by retrieved contexts."""
    available_citations = {
        str(context["citation_label"])
        for context in contexts
        if str(context.get("citation_label", "")).strip()
    }
    used_citations = {
        str(citation)
        for citation in answer.get("used_citations", [])
        if str(citation).strip()
    }

    missing_citations = []
    if available_citations and not used_citations:
        missing_citations = sorted(available_citations)

    unsupported_citations = sorted(used_citations - available_citations)
    notes = []
    if not available_citations:
        notes.append("No retrieved context citations were available.")
    if missing_citations:
        notes.append("Answer did not include a citation despite available context.")
    if unsupported_citations:
        notes.append("Answer included citations that were not retrieved.")
    if not notes:
        notes.append("All used citations are supported by retrieved context.")

    return {
        "is_valid": not missing_citations and not unsupported_citations,
        "missing_citations": missing_citations,
        "unsupported_citations": unsupported_citations,
        "citation_count": len(used_citations),
        "notes": notes,
    }
