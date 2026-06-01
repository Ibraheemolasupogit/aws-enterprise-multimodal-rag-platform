"""Deterministic local answer guardrails."""

from __future__ import annotations

import re


def _contains_pattern(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def check_answer_safety(
    answer: dict[str, object],
    contexts: list[dict[str, object]],
    citation_validation: dict[str, object],
    guardrails_config: dict[str, object],
) -> dict[str, object]:
    """Inspect generated answers after citation validation."""
    answer_text = str(answer.get("answer_text", ""))
    triggered_rules = []
    notes = []
    risk_level = "low"
    is_allowed = True
    context_exists = bool(contexts)

    if citation_validation.get("unsupported_citations"):
        triggered_rules.append("unsupported_citation_reference")
    if (
        context_exists
        and bool(guardrails_config["require_citations_when_context_exists"])
        and int(citation_validation.get("citation_count", 0)) == 0
    ):
        triggered_rules.append("missing_required_citation")
    if (
        bool(guardrails_config["hallucination_risk_on_invalid_citations"])
        and not bool(citation_validation["is_valid"])
    ):
        triggered_rules.append("hallucination_risk_invalid_citations")

    if _contains_pattern(answer_text, list(guardrails_config["sensitive_data_patterns"])):
        triggered_rules.append("sensitive_data_leakage_placeholder")
    if _contains_pattern(answer_text, list(guardrails_config["unsafe_answer_patterns"])):
        triggered_rules.append("unsafe_content_placeholder")

    if not context_exists and "insufficient evidence" in answer_text.lower():
        notes.append("Insufficient-evidence response is allowed because no context exists.")

    blocking_rules = {
        "unsupported_citation_reference",
        "missing_required_citation",
        "hallucination_risk_invalid_citations",
        "sensitive_data_leakage_placeholder",
        "unsafe_content_placeholder",
    }
    if any(rule in blocking_rules for rule in triggered_rules):
        risk_level = "high"
        is_allowed = False
    elif triggered_rules:
        risk_level = "medium"

    final_answer_text = answer_text
    if not is_allowed:
        final_answer_text = (
            "I cannot provide this response because the local safety checks "
            "identified unsupported or unsafe content."
        )

    if not notes and not triggered_rules:
        notes.append("Answer passed local deterministic guardrail checks.")

    return {
        "is_allowed": is_allowed,
        "risk_level": risk_level,
        "triggered_rules": triggered_rules,
        "final_answer_text": final_answer_text,
        "notes": notes,
    }
