"""CLI-friendly local retrieval runner."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from enterprise_rag_platform.ingestion.ingestion_runner import (
    DEFAULT_CONFIG_PATH,
    PROJECT_ROOT,
    load_config,
    resolve_project_path,
    save_json,
)
from enterprise_rag_platform.retrieval.vector_store import LocalVectorStore


SAMPLE_QUERY = "How should AI-generated responses handle source material?"


def write_retrieval_report(
    output_path: Path,
    query: str,
    results: list[dict[str, object]],
) -> None:
    """Write a lightweight local retrieval report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    report = f"""# Retrieval Report

Generated at: {generated_at}

## Query

{query}

## Results

"""

    for result in results:
        report += (
            f"- Rank {result['rank']}: `{result['chunk_id']}` from "
            f"`{result['source_file']}` "
            f"(score: {result['similarity_score']})\n"
        )

    output_path.write_text(report, encoding="utf-8")


def run_retrieval(config_path: str | Path = DEFAULT_CONFIG_PATH) -> dict[str, Path | int]:
    """Run local vector similarity search using a sample query."""
    config = load_config(config_path)
    embedding_output_path = resolve_project_path(str(config["embedding_output_path"]))
    retrieval_results_output_path = resolve_project_path(
        str(config["retrieval_results_output_path"])
    )
    retrieval_report_path = PROJECT_ROOT / "reports" / "sample" / "retrieval_report.md"
    embedding_dimension = int(config["embedding_dimension"])
    retrieval_top_k = int(config["retrieval_top_k"])

    vector_store = LocalVectorStore.from_json(
        embedding_output_path,
        embedding_dimension=embedding_dimension,
    )
    results = vector_store.search(SAMPLE_QUERY, top_k=retrieval_top_k)

    save_json(results, retrieval_results_output_path)
    write_retrieval_report(retrieval_report_path, SAMPLE_QUERY, results)

    return {
        "result_count": len(results),
        "retrieval_results_output_path": retrieval_results_output_path,
        "retrieval_report_path": retrieval_report_path,
    }


def main() -> None:
    """Run local retrieval and print output locations."""
    result = run_retrieval()
    print(f"Retrieved {result['result_count']} results.")
    print(f"Retrieval results JSON: {result['retrieval_results_output_path']}")
    print(f"Retrieval report: {result['retrieval_report_path']}")


if __name__ == "__main__":
    main()
