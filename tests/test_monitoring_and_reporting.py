import csv
import json
from pathlib import Path

from enterprise_rag_platform.embeddings.embedding_runner import run_embedding
from enterprise_rag_platform.evaluation.evaluation_runner import run_evaluation
from enterprise_rag_platform.generation.rag_runner import run_rag_generation
from enterprise_rag_platform.guardrails.guardrail_runner import run_guardrails
from enterprise_rag_platform.ingestion.ingestion_runner import load_config, run_ingestion
from enterprise_rag_platform.monitoring.metrics_collector import (
    collect_dashboard_metrics,
)
from enterprise_rag_platform.monitoring.monitoring_runner import run_monitoring
from enterprise_rag_platform.monitoring.pipeline_monitor import inspect_pipeline_health
from enterprise_rag_platform.retrieval.retrieval_runner import run_retrieval


ROOT = Path(__file__).resolve().parents[1]


def _prepare_artifacts():
    run_ingestion()
    run_embedding()
    run_retrieval()
    run_rag_generation()
    run_evaluation()
    run_guardrails("What does the policy say about data protection?")


def test_pipeline_monitor_returns_health_summary():
    _prepare_artifacts()
    health = inspect_pipeline_health(load_config())

    assert health["pipeline_health_status"] in {"healthy", "degraded", "incomplete"}
    assert "total_documents" in health
    assert "missing_artifacts" in health


def test_missing_artifacts_are_detected():
    config = load_config()
    config["generated_answer_output_path"] = "outputs/sample/does_not_exist.json"

    health = inspect_pipeline_health(config)

    assert health["pipeline_health_status"] == "incomplete"
    assert health["missing_artifacts"]


def test_dashboard_metrics_are_generated():
    _prepare_artifacts()
    config = load_config()
    health = inspect_pipeline_health(config)
    metrics = collect_dashboard_metrics(config, health)

    assert metrics["pipeline_health_status"] == health["pipeline_health_status"]
    assert "retrieval_result_count" in metrics
    assert "average_overall_score" in metrics


def test_evaluation_averages_are_between_zero_and_one():
    _prepare_artifacts()
    config = load_config()
    health = inspect_pipeline_health(config)
    metrics = collect_dashboard_metrics(config, health)

    assert 0.0 <= metrics["average_overall_score"] <= 1.0
    assert 0.0 <= metrics["average_keyword_coverage_score"] <= 1.0
    assert 0.0 <= metrics["average_groundedness_score"] <= 1.0
    assert 0.0 <= metrics["average_answer_completeness_score"] <= 1.0


def test_guardrail_metrics_are_included():
    _prepare_artifacts()
    config = load_config()
    health = inspect_pipeline_health(config)
    metrics = collect_dashboard_metrics(config, health)

    assert "query_allowed" in metrics
    assert "query_risk_level" in metrics
    assert "answer_allowed" in metrics
    assert "answer_risk_level" in metrics
    assert "triggered_rule_count" in metrics


def test_dashboard_metrics_json_is_created():
    _prepare_artifacts()
    result = run_monitoring()
    output_path = result["dashboard_metrics_json_path"]
    metrics = json.loads(output_path.read_text(encoding="utf-8"))

    assert output_path == ROOT / "outputs" / "sample" / "dashboard_metrics.json"
    assert output_path.is_file()
    assert metrics["pipeline_health_status"]


def test_dashboard_metrics_csv_is_created():
    _prepare_artifacts()
    result = run_monitoring()
    output_path = result["dashboard_metrics_csv_path"]

    with output_path.open("r", encoding="utf-8", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert output_path == ROOT / "outputs" / "sample" / "dashboard_metrics.csv"
    assert output_path.is_file()
    assert rows


def test_pipeline_health_json_is_created():
    _prepare_artifacts()
    result = run_monitoring()
    output_path = result["pipeline_health_output_path"]
    health = json.loads(output_path.read_text(encoding="utf-8"))

    assert output_path == ROOT / "outputs" / "sample" / "pipeline_health.json"
    assert output_path.is_file()
    assert health["pipeline_health_status"]


def test_monitoring_report_is_created():
    _prepare_artifacts()
    result = run_monitoring()
    output_path = result["monitoring_report_path"]

    assert output_path == ROOT / "reports" / "sample" / "monitoring_report.md"
    assert output_path.is_file()


def test_report_contains_core_sections():
    _prepare_artifacts()
    result = run_monitoring()
    report = result["monitoring_report_path"].read_text(encoding="utf-8")

    assert "Pipeline Health" in report
    assert "Evaluation Summary" in report
    assert "Retrieval Summary" in report
    assert "Generation Summary" in report
    assert "Guardrail Summary" in report
