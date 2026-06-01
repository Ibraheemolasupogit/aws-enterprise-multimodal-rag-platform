"""CLI-friendly local guardrail runner."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from enterprise_rag_platform.citations.citation_validator import validate_citations
from enterprise_rag_platform.generation.mock_generator import generate_mock_answer
from enterprise_rag_platform.generation.prompt_builder import (
    DEFAULT_GENERATION_CONSTRAINTS,
    build_rag_prompt,
)
from enterprise_rag_platform.guardrails.answer_guardrail import check_answer_safety
from enterprise_rag_platform.guardrails.query_guardrail import check_query_safety
from enterprise_rag_platform.ingestion.ingestion_runner import (
    DEFAULT_CONFIG_PATH,
    PROJECT_ROOT,
    load_config,
    resolve_project_path,
    save_json,
)
from enterprise_rag_platform.retrieval.retrieval_orchestrator import (
    run_retrieval_orchestration,
)


DEFAULT_GUARDRAILS_CONFIG_PATH = PROJECT_ROOT / "config" / "guardrails_config.yaml"


def load_guardrails_config(
    config_path: str | Path = DEFAULT_GUARDRAILS_CONFIG_PATH,
) -> dict[str, object]:
    """Load guardrail settings from YAML."""
    with Path(config_path).open("r", encoding="utf-8") as config_file:
        payload = yaml.safe_load(config_file) or {}
    return dict(payload.get("guardrails", payload))


def build_guarded_refusal(
    raw_query: str,
    query_guardrail: dict[str, object],
) -> dict[str, object]:
    """Create a guarded refusal payload when query checks block retrieval."""
    return {
        "query": {
            "raw_query": raw_query,
            "safe_query": query_guardrail["safe_query"],
        },
        "query_guardrail": query_guardrail,
        "retrieval_response": None,
        "answer": {
            "answer_text": (
                "I cannot process this request because it did not pass local "
                f"safety checks: {query_guardrail['refusal_reason']}"
            ),
            "used_citations": [],
            "generation_mode": "guarded_refusal",
        },
        "citation_validation": None,
        "answer_guardrail": None,
        "final_response": {
            "is_allowed": False,
            "final_answer_text": (
                "I cannot process this request because it did not pass local "
                f"safety checks: {query_guardrail['refusal_reason']}"
            ),
        },
    }


def write_guardrail_report(output_path: Path, payload: dict[str, object]) -> None:
    """Write a Markdown guardrail report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    query_guardrail = payload["query_guardrail"]
    answer_guardrail = payload.get("answer_guardrail")
    final_response = payload["final_response"]

    report = f"""# Guardrail Report

Generated at: {generated_at}

## Query Guardrail

- Allowed: {query_guardrail["is_allowed"]}
- Risk level: {query_guardrail["risk_level"]}
- Triggered rules: {query_guardrail["triggered_rules"]}

## Answer Guardrail

"""

    if answer_guardrail:
        report += (
            f"- Allowed: {answer_guardrail['is_allowed']}\n"
            f"- Risk level: {answer_guardrail['risk_level']}\n"
            f"- Triggered rules: {answer_guardrail['triggered_rules']}\n"
        )
    else:
        report += "- Not run because query was blocked.\n"

    report += f"""
## Final Guarded Response

{final_response["final_answer_text"]}
"""

    output_path.write_text(report, encoding="utf-8")


def run_guardrails(
    raw_query: str | None = None,
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    guardrails_config_path: str | Path = DEFAULT_GUARDRAILS_CONFIG_PATH,
) -> dict[str, Path | bool]:
    """Run query guardrails, local RAG, and answer guardrails."""
    rag_config = load_config(config_path)
    guardrails_config = load_guardrails_config(guardrails_config_path)
    query = raw_query or str(rag_config["sample_query"])

    query_guardrail = check_query_safety(query, guardrails_config)
    if not query_guardrail["is_allowed"]:
        payload = build_guarded_refusal(query, query_guardrail)
    else:
        retrieval_response = run_retrieval_orchestration(query, config_path=config_path)
        prompt = build_rag_prompt(
            query=retrieval_response["query"],
            contexts=retrieval_response["contexts"],
            system_instruction=str(rag_config["system_instruction"]),
            generation_constraints=DEFAULT_GENERATION_CONSTRAINTS
            + [f"Answer style: {rag_config['answer_style']}"],
            max_context_blocks=int(rag_config["max_context_blocks"]),
        )
        answer = generate_mock_answer(prompt)
        citation_validation = validate_citations(answer, retrieval_response["contexts"])
        answer_guardrail = check_answer_safety(
            answer,
            retrieval_response["contexts"],
            citation_validation,
            guardrails_config,
        )
        payload = {
            "query": retrieval_response["query"],
            "query_guardrail": query_guardrail,
            "retrieval_response": retrieval_response,
            "answer": answer,
            "citation_validation": citation_validation,
            "answer_guardrail": answer_guardrail,
            "final_response": {
                "is_allowed": bool(answer_guardrail["is_allowed"]),
                "final_answer_text": answer_guardrail["final_answer_text"],
            },
        }

    output_path = resolve_project_path(str(rag_config["guardrail_results_output_path"]))
    report_path = resolve_project_path(str(rag_config["guardrail_report_path"]))
    save_json(payload, output_path)
    write_guardrail_report(report_path, payload)

    return {
        "is_allowed": bool(payload["final_response"]["is_allowed"]),
        "guardrail_results_output_path": output_path,
        "guardrail_report_path": report_path,
    }


def main() -> None:
    """Run local guardrails and print output locations."""
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    result = run_guardrails(raw_query=query)
    print(f"Guarded response allowed: {result['is_allowed']}")
    print(f"Guardrail results JSON: {result['guardrail_results_output_path']}")
    print(f"Guardrail report: {result['guardrail_report_path']}")


if __name__ == "__main__":
    main()
