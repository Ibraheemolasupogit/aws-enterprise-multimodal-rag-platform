import csv
import json
from pathlib import Path

import pytest

from enterprise_rag_platform.embeddings.embedding_runner import run_embedding
from enterprise_rag_platform.evaluation.evaluation_dataset_loader import (
    load_evaluation_dataset,
)
from enterprise_rag_platform.evaluation.evaluation_runner import run_evaluation
from enterprise_rag_platform.evaluation.rag_evaluator import evaluate_records
from enterprise_rag_platform.ingestion.ingestion_runner import load_config, run_ingestion


ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "data" / "evaluation" / "sample_questions.csv"


def _prepare_pipeline():
    run_ingestion()
    run_embedding()


def test_evaluation_dataset_loader_loads_records():
    records = load_evaluation_dataset(DATASET_PATH)

    assert len(records) >= 5
    assert records[0]["question_id"]
    assert records[0]["question"]


def test_required_columns_are_validated(tmp_path):
    invalid_dataset = tmp_path / "invalid.csv"
    invalid_dataset.write_text("question_id,question\nq1,Test question\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing columns"):
        load_evaluation_dataset(invalid_dataset)


def test_expected_keywords_are_parsed_correctly():
    records = load_evaluation_dataset(DATASET_PATH)

    assert isinstance(records[0]["expected_keywords"], list)
    assert records[0]["expected_keywords"]


def test_evaluator_returns_scores_for_each_question():
    _prepare_pipeline()
    config = load_config()
    records = load_evaluation_dataset(DATASET_PATH)

    results = evaluate_records(records, config=config)

    assert len(results) == len(records)
    assert "overall_score" in results[0]


def test_keyword_coverage_score_is_between_zero_and_one():
    _prepare_pipeline()
    config = load_config()
    records = load_evaluation_dataset(DATASET_PATH)

    results = evaluate_records(records, config=config)

    assert all(0.0 <= result["keyword_coverage_score"] <= 1.0 for result in results)


def test_overall_score_is_between_zero_and_one():
    _prepare_pipeline()
    config = load_config()
    records = load_evaluation_dataset(DATASET_PATH)

    results = evaluate_records(records, config=config)

    assert all(0.0 <= result["overall_score"] <= 1.0 for result in results)


def test_citation_valid_is_included():
    _prepare_pipeline()
    config = load_config()
    records = load_evaluation_dataset(DATASET_PATH)

    results = evaluate_records(records, config=config)

    assert "citation_valid" in results[0]


def test_evaluation_json_output_is_created():
    _prepare_pipeline()
    result = run_evaluation()

    output_path = result["evaluation_results_json_path"]
    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert output_path == ROOT / "outputs" / "sample" / "evaluation_results.json"
    assert output_path.is_file()
    assert payload["results"]


def test_evaluation_csv_output_is_created():
    _prepare_pipeline()
    result = run_evaluation()

    output_path = result["evaluation_results_csv_path"]
    with output_path.open("r", encoding="utf-8", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert output_path == ROOT / "outputs" / "sample" / "evaluation_results.csv"
    assert output_path.is_file()
    assert rows


def test_evaluation_report_is_created():
    _prepare_pipeline()
    result = run_evaluation()

    output_path = result["evaluation_report_path"]

    assert output_path == ROOT / "reports" / "sample" / "rag_evaluation_report.md"
    assert output_path.is_file()
    assert "RAG Evaluation Report" in output_path.read_text(encoding="utf-8")


def test_out_of_scope_question_is_handled_safely():
    _prepare_pipeline()
    config = load_config()
    records = load_evaluation_dataset(DATASET_PATH)
    out_of_scope_records = [
        record
        for record in records
        if record["evaluation_category"] == "insufficient_evidence"
    ]

    results = evaluate_records(out_of_scope_records, config=config)

    assert results
    assert results[0]["insufficient_evidence_handled"] is True
    assert "Insufficient evidence" in results[0]["answer_text"]
