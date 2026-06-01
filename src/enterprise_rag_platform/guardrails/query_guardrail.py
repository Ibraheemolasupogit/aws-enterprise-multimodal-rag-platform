"""Deterministic local query guardrails."""

from __future__ import annotations

import re


def _matches_any_pattern(text: str, patterns: list[str]) -> list[str]:
    return [
        pattern
        for pattern in patterns
        if re.search(pattern, text, flags=re.IGNORECASE)
    ]


def check_query_safety(
    raw_query: str,
    guardrails_config: dict[str, object],
) -> dict[str, object]:
    """Inspect a user query before retrieval."""
    safe_query = re.sub(r"\s+", " ", raw_query).strip()
    triggered_rules = []
    notes = []
    refusal_reason = None
    risk_level = "low"

    minimum_query_words = int(guardrails_config["minimum_query_words"])
    if not safe_query:
        triggered_rules.append("empty_query")
        refusal_reason = "Query is empty."
    elif len(safe_query.split()) < minimum_query_words:
        triggered_rules.append("too_short_query")
        refusal_reason = f"Query must contain at least {minimum_query_words} words."

    prompt_injection_matches = _matches_any_pattern(
        safe_query,
        list(guardrails_config["prompt_injection_patterns"]),
    )
    if prompt_injection_matches:
        triggered_rules.append("prompt_injection_attempt")
        refusal_reason = "Query appears to request instruction override or prompt disclosure."

    blocked_matches = _matches_any_pattern(
        safe_query,
        list(guardrails_config["blocked_query_patterns"]),
    )
    if blocked_matches:
        triggered_rules.append("blocked_query_pattern")
        refusal_reason = "Query matches a blocked safety pattern."

    sensitive_matches = _matches_any_pattern(
        safe_query,
        list(guardrails_config["sensitive_data_patterns"]),
    )
    if sensitive_matches:
        triggered_rules.append("sensitive_data_request")
        refusal_reason = "Query appears to request sensitive data."

    out_of_scope_patterns = list(guardrails_config.get("out_of_scope_patterns", []))
    if _matches_any_pattern(safe_query, out_of_scope_patterns):
        triggered_rules.append("out_of_scope_enterprise_knowledge")
        notes.append("Query may be outside the enterprise knowledge scope.")

    is_blocking = any(
        rule
        in {
            "empty_query",
            "too_short_query",
            "prompt_injection_attempt",
            "blocked_query_pattern",
            "sensitive_data_request",
        }
        for rule in triggered_rules
    )

    if is_blocking:
        risk_level = "high"
    elif triggered_rules:
        risk_level = "medium"

    if not notes and not triggered_rules:
        notes.append("Query passed local deterministic guardrail checks.")

    return {
        "is_allowed": not is_blocking,
        "risk_level": risk_level,
        "triggered_rules": triggered_rules,
        "safe_query": safe_query,
        "refusal_reason": refusal_reason,
        "notes": notes,
    }
