"""CLI-friendly local RAG evaluation runner."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

from enterprise_rag_platform.evaluation.evaluation_dataset_loader import (
    load_evaluation_dataset,
)
from enterprise_rag_platform.evaluation.rag_evaluator import evaluate_records
from enterprise_rag_platform.ingestion.ingestion_runner import (
    DEFAULT_CONFIG_PATH,
    load_config,
    resolve_project_path,
    save_json,
)


SUMMARY_FIELDS = [
    "question_id",
    "evaluation_category",
    "retrieval_hit",
    "citation_valid",
    "keyword_coverage_score",
    "groundedness_score",
    "answer_completeness_score",
    "insufficient_evidence_handled",
    "overall_score",
    "latency_ms",
]


def write_summary_csv(results: list[dict[str, object]], output_path: Path) -> None:
    """Write compact evaluation summary CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        for result in results:
            writer.writerow({field: result[field] for field in SUMMARY_FIELDS})


def write_evaluation_report(
    results: list[dict[str, object]],
    output_path: Path,
    minimum_overall_score: float,
) -> None:
    """Write a Markdown evaluation report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    average_score = (
        sum(float(result["overall_score"]) for result in results) / len(results)
        if results
        else 0.0
    )
    pass_count = sum(
        1 for result in results if float(result["overall_score"]) >= minimum_overall_score
    )

    report = f"""# RAG Evaluation Report

Generated at: {generated_at}

## Summary

- Questions evaluated: {len(results)}
- Average overall score: {average_score:.4f}
- Minimum target score: {minimum_overall_score:.4f}
- Questions meeting target: {pass_count}

## Results

"""

    for result in results:
        report += (
            f"- `{result['question_id']}` ({result['evaluation_category']}): "
            f"overall={result['overall_score']}, "
            f"retrieval_hit={result['retrieval_hit']}, "
            f"citation_valid={result['citation_valid']}, "
            f"keyword_coverage={result['keyword_coverage_score']}\n"
        )

    output_path.write_text(report, encoding="utf-8")


def run_evaluation(
    config_path: str | Path = DEFAULT_CONFIG_PATH,
) -> dict[str, Path | int | float]:
    """Run local deterministic RAG evaluation."""
    config = load_config(config_path)
    dataset_path = resolve_project_path(str(config["evaluation_questions_path"]))
    results_json_path = resolve_project_path(str(config["evaluation_results_json_path"]))
    results_csv_path = resolve_project_path(str(config["evaluation_results_csv_path"]))
    report_path = resolve_project_path(str(config["evaluation_report_path"]))

    records = load_evaluation_dataset(dataset_path)
    results = evaluate_records(records, config=config, config_path=str(config_path))
    minimum_overall_score = float(config["evaluation_minimum_overall_score"])

    payload = {
        "evaluation_metadata": {
            "question_count": len(records),
            "minimum_overall_score": minimum_overall_score,
            "average_overall_score": round(
                sum(float(result["overall_score"]) for result in results) / len(results),
                4,
            )
            if results
            else 0.0,
        },
        "results": results,
    }

    save_json(payload, results_json_path)
    write_summary_csv(results, results_csv_path)
    write_evaluation_report(results, report_path, minimum_overall_score)

    return {
        "question_count": len(records),
        "average_overall_score": payload["evaluation_metadata"]["average_overall_score"],
        "evaluation_results_json_path": results_json_path,
        "evaluation_results_csv_path": results_csv_path,
        "evaluation_report_path": report_path,
    }


def main() -> None:
    """Run local evaluation and print output locations."""
    result = run_evaluation()
    print(f"Evaluated {result['question_count']} questions.")
    print(f"Average overall score: {result['average_overall_score']}")
    print(f"Evaluation JSON: {result['evaluation_results_json_path']}")
    print(f"Evaluation CSV: {result['evaluation_results_csv_path']}")
    print(f"Evaluation report: {result['evaluation_report_path']}")


if __name__ == "__main__":
    main()
