"""CLI-friendly local monitoring and reporting runner."""

from __future__ import annotations

import csv
from pathlib import Path

from enterprise_rag_platform.ingestion.ingestion_runner import (
    DEFAULT_CONFIG_PATH,
    load_config,
    resolve_project_path,
    save_json,
)
from enterprise_rag_platform.monitoring.metrics_collector import (
    collect_dashboard_metrics,
)
from enterprise_rag_platform.monitoring.pipeline_monitor import inspect_pipeline_health
from enterprise_rag_platform.reporting.report_builder import write_monitoring_report


def write_metrics_csv(metrics: dict[str, object], output_path: Path) -> None:
    """Write dashboard metrics in key-value CSV format."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["metric", "value"])
        writer.writeheader()
        for key, value in metrics.items():
            writer.writerow({"metric": key, "value": value})


def run_monitoring(
    config_path: str | Path = DEFAULT_CONFIG_PATH,
) -> dict[str, Path | str]:
    """Inspect local artifacts and produce monitoring outputs."""
    config = load_config(config_path)
    pipeline_health = inspect_pipeline_health(config)
    metrics = collect_dashboard_metrics(config, pipeline_health)

    pipeline_health_output_path = resolve_project_path(
        str(config["pipeline_health_output_path"])
    )
    dashboard_metrics_json_path = resolve_project_path(
        str(config["dashboard_metrics_json_path"])
    )
    dashboard_metrics_csv_path = resolve_project_path(
        str(config["dashboard_metrics_csv_path"])
    )
    monitoring_report_path = resolve_project_path(str(config["monitoring_report_path"]))

    save_json(pipeline_health, pipeline_health_output_path)
    save_json(metrics, dashboard_metrics_json_path)
    write_metrics_csv(metrics, dashboard_metrics_csv_path)
    write_monitoring_report(monitoring_report_path, pipeline_health, metrics)

    return {
        "pipeline_health_status": pipeline_health["pipeline_health_status"],
        "pipeline_health_output_path": pipeline_health_output_path,
        "dashboard_metrics_json_path": dashboard_metrics_json_path,
        "dashboard_metrics_csv_path": dashboard_metrics_csv_path,
        "monitoring_report_path": monitoring_report_path,
    }


def main() -> None:
    """Run local monitoring and print output locations."""
    result = run_monitoring()
    print(f"Pipeline health status: {result['pipeline_health_status']}")
    print(f"Pipeline health JSON: {result['pipeline_health_output_path']}")
    print(f"Dashboard metrics JSON: {result['dashboard_metrics_json_path']}")
    print(f"Dashboard metrics CSV: {result['dashboard_metrics_csv_path']}")
    print(f"Monitoring report: {result['monitoring_report_path']}")


if __name__ == "__main__":
    main()
