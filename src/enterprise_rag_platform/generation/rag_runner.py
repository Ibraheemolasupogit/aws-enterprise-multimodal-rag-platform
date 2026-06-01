"""CLI-friendly local mock RAG generation runner."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

from enterprise_rag_platform.citations.citation_validator import validate_citations
from enterprise_rag_platform.generation.mock_generator import generate_mock_answer
from enterprise_rag_platform.generation.prompt_builder import (
    DEFAULT_GENERATION_CONSTRAINTS,
    build_rag_prompt,
)
from enterprise_rag_platform.ingestion.ingestion_runner import (
    DEFAULT_CONFIG_PATH,
    load_config,
    resolve_project_path,
    save_json,
)
from enterprise_rag_platform.retrieval.retrieval_orchestrator import (
    run_retrieval_orchestration,
)


def write_rag_generation_report(
    output_path: Path,
    retrieval_response: dict[str, object],
    prompt: dict[str, object],
    answer: dict[str, object],
    citation_validation: dict[str, object],
) -> None:
    """Write a lightweight report for local mock RAG generation."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    query = retrieval_response["query"]

    report = f"""# RAG Generation Report

Generated at: {generated_at}

## Query

{query["normalized_query"]}

## Summary

- Retrieval contexts: {retrieval_response["result_count"]}
- Prompt ID: {prompt["prompt_id"]}
- Answer ID: {answer["answer_id"]}
- Generation mode: {answer["generation_mode"]}
- Citation validation passed: {citation_validation["is_valid"]}

## Answer

{answer["answer_text"]}

## Citations

"""

    if answer["used_citations"]:
        for citation in answer["used_citations"]:
            report += f"- {citation}\n"
    else:
        report += "- None\n"

    report += "\n## Validation Notes\n\n"
    for note in citation_validation["notes"]:
        report += f"- {note}\n"

    output_path.write_text(report, encoding="utf-8")


def run_rag_generation(
    raw_query: str | None = None,
    config_path: str | Path = DEFAULT_CONFIG_PATH,
) -> dict[str, Path | int | bool]:
    """Run local retrieval, prompt assembly, mock generation, and citation validation."""
    config = load_config(config_path)
    query = raw_query or str(config["sample_query"])

    retrieval_response = run_retrieval_orchestration(query, config_path=config_path)
    prompt = build_rag_prompt(
        query=retrieval_response["query"],
        contexts=retrieval_response["contexts"],
        system_instruction=str(config["system_instruction"]),
        generation_constraints=DEFAULT_GENERATION_CONSTRAINTS
        + [f"Answer style: {config['answer_style']}"],
        max_context_blocks=int(config["max_context_blocks"]),
    )
    answer = generate_mock_answer(prompt)
    citation_validation = validate_citations(answer, retrieval_response["contexts"])
    generated_answer_payload = {
        "query": retrieval_response["query"],
        "answer": answer,
        "citation_validation": citation_validation,
    }

    rag_prompt_output_path = resolve_project_path(str(config["rag_prompt_output_path"]))
    generated_answer_output_path = resolve_project_path(
        str(config["generated_answer_output_path"])
    )
    report_output_path = resolve_project_path(str(config["rag_generation_report_path"]))

    save_json(prompt, rag_prompt_output_path)
    save_json(generated_answer_payload, generated_answer_output_path)
    write_rag_generation_report(
        report_output_path,
        retrieval_response=retrieval_response,
        prompt=prompt,
        answer=answer,
        citation_validation=citation_validation,
    )

    return {
        "context_count": int(retrieval_response["result_count"]),
        "citation_validation_passed": bool(citation_validation["is_valid"]),
        "rag_prompt_output_path": rag_prompt_output_path,
        "generated_answer_output_path": generated_answer_output_path,
        "rag_generation_report_path": report_output_path,
    }


def main() -> None:
    """Run local mock RAG generation and print output locations."""
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    result = run_rag_generation(raw_query=query)
    print(f"Built prompt with {result['context_count']} contexts.")
    print(f"Citation validation passed: {result['citation_validation_passed']}")
    print(f"RAG prompt JSON: {result['rag_prompt_output_path']}")
    print(f"Generated answer JSON: {result['generated_answer_output_path']}")
    print(f"RAG generation report: {result['rag_generation_report_path']}")


if __name__ == "__main__":
    main()
