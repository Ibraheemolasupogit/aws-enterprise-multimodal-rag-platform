"""CLI-friendly local retrieval runner."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

from enterprise_rag_platform.ingestion.ingestion_runner import (
    DEFAULT_CONFIG_PATH,
    load_config,
    resolve_project_path,
    save_json,
)
from enterprise_rag_platform.retrieval.retrieval_orchestrator import (
    run_retrieval_orchestration,
)


def write_retrieval_context_report(
    output_path: Path,
    retrieval_response: dict[str, object],
) -> None:
    """Write a lightweight local retrieval context report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    query = retrieval_response["query"]
    contexts = retrieval_response["contexts"]
    parameters = retrieval_response["retrieval_parameters"]

    report = f"""# Retrieval Context Report

Generated at: {generated_at}

## Query

{query["normalized_query"]}

## Parameters

- Top K: {parameters["top_k"]}
- Minimum similarity score: {parameters["minimum_similarity_score"]}
- Embedding dimension: {parameters["embedding_dimension"]}

## Results

"""

    if not contexts:
        report += f"{retrieval_response['no_result_reason']}\n"
    for context in contexts:
        report += (
            f"- Rank {context['rank']}: {context['citation_label']} "
            f"(score: {context['similarity_score']})\n"
        )

    output_path.write_text(report, encoding="utf-8")


def run_retrieval(
    raw_query: str | None = None,
    config_path: str | Path = DEFAULT_CONFIG_PATH,
) -> dict[str, Path | int]:
    """Run local retrieval orchestration and write context artifacts."""
    config = load_config(config_path)
    query = raw_query or str(config["sample_query"])
    retrieval_context_output_path = resolve_project_path(
        str(config["retrieval_context_output_path"])
    )
    retrieval_context_report_path = resolve_project_path(
        str(config["retrieval_context_report_path"])
    )
    retrieval_results_output_path = resolve_project_path(
        str(config["retrieval_results_output_path"])
    )

    retrieval_response = run_retrieval_orchestration(
        query,
        config_path=config_path,
    )
    contexts = retrieval_response["contexts"]

    save_json(retrieval_response, retrieval_context_output_path)
    save_json(contexts, retrieval_results_output_path)
    write_retrieval_context_report(retrieval_context_report_path, retrieval_response)

    return {
        "result_count": int(retrieval_response["result_count"]),
        "retrieval_context_output_path": retrieval_context_output_path,
        "retrieval_context_report_path": retrieval_context_report_path,
        "retrieval_results_output_path": retrieval_results_output_path,
    }


def main() -> None:
    """Run local retrieval and print output locations."""
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    result = run_retrieval(raw_query=query)
    print(f"Retrieved {result['result_count']} results.")
    print(f"Retrieval context JSON: {result['retrieval_context_output_path']}")
    print(f"Retrieval context report: {result['retrieval_context_report_path']}")


if __name__ == "__main__":
    main()
