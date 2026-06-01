import json
from pathlib import Path

from enterprise_rag_platform.citations.citation_validator import validate_citations
from enterprise_rag_platform.embeddings.embedding_runner import run_embedding
from enterprise_rag_platform.generation.mock_generator import generate_mock_answer
from enterprise_rag_platform.generation.prompt_builder import build_rag_prompt
from enterprise_rag_platform.generation.rag_runner import run_rag_generation
from enterprise_rag_platform.ingestion.ingestion_runner import run_ingestion
from enterprise_rag_platform.retrieval.retrieval_orchestrator import (
    run_retrieval_orchestration,
)


ROOT = Path(__file__).resolve().parents[1]


def _sample_query_and_contexts():
    run_ingestion()
    run_embedding()
    retrieval_response = run_retrieval_orchestration(
        "How should AI-generated responses handle source material?"
    )
    return retrieval_response["query"], retrieval_response["contexts"]


def test_prompt_builder_creates_prompt_id_and_assembled_prompt():
    query, contexts = _sample_query_and_contexts()

    prompt = build_rag_prompt(
        query=query,
        contexts=contexts,
        system_instruction="Answer only from context.",
    )

    assert prompt["prompt_id"].startswith("prompt_")
    assert prompt["assembled_prompt"]
    assert "answer only from context" in prompt["assembled_prompt"].lower()


def test_context_blocks_preserve_citation_labels():
    query, contexts = _sample_query_and_contexts()

    prompt = build_rag_prompt(
        query=query,
        contexts=contexts,
        system_instruction="Answer only from context.",
    )

    assert prompt["context_blocks"]
    assert prompt["context_blocks"][0]["citation_label"] == contexts[0]["citation_label"]
    assert prompt["context_blocks"][0]["chunk_id"] == contexts[0]["chunk_id"]


def test_mock_generator_returns_answer_text():
    query, contexts = _sample_query_and_contexts()
    prompt = build_rag_prompt(query, contexts, "Answer only from context.")

    answer = generate_mock_answer(prompt)

    assert answer["answer_text"]
    assert answer["generation_mode"] == "mock_local_generation"


def test_generated_answer_uses_only_retrieved_citations():
    query, contexts = _sample_query_and_contexts()
    prompt = build_rag_prompt(query, contexts, "Answer only from context.")
    answer = generate_mock_answer(prompt)
    available_citations = {context["citation_label"] for context in contexts}

    assert set(answer["used_citations"]).issubset(available_citations)


def test_insufficient_evidence_response_when_no_context_exists():
    query = {
        "query_id": "query_empty",
        "normalized_query": "What does the policy say?",
    }
    prompt = build_rag_prompt(query, [], "Answer only from context.")

    answer = generate_mock_answer(prompt)

    assert "Insufficient evidence" in answer["answer_text"]
    assert answer["used_citations"] == []


def test_citation_validator_detects_valid_citations():
    query, contexts = _sample_query_and_contexts()
    prompt = build_rag_prompt(query, contexts, "Answer only from context.")
    answer = generate_mock_answer(prompt)

    validation = validate_citations(answer, contexts)

    assert validation["is_valid"] is True
    assert validation["unsupported_citations"] == []


def test_citation_validator_detects_unsupported_citations():
    _, contexts = _sample_query_and_contexts()
    answer = {
        "used_citations": ["[unknown.md | chunk_9999]"],
    }

    validation = validate_citations(answer, contexts)

    assert validation["is_valid"] is False
    assert validation["unsupported_citations"] == ["[unknown.md | chunk_9999]"]


def test_rag_runner_creates_generated_answer_json():
    run_ingestion()
    run_embedding()
    result = run_rag_generation()

    output_path = result["generated_answer_output_path"]
    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert output_path == ROOT / "outputs" / "sample" / "generated_answer.json"
    assert output_path.is_file()
    assert payload["answer"]["answer_text"]


def test_rag_prompt_json_is_created():
    run_ingestion()
    run_embedding()
    result = run_rag_generation()

    output_path = result["rag_prompt_output_path"]
    prompt = json.loads(output_path.read_text(encoding="utf-8"))

    assert output_path == ROOT / "outputs" / "sample" / "rag_prompt.json"
    assert output_path.is_file()
    assert prompt["assembled_prompt"]


def test_rag_generation_report_is_created():
    run_ingestion()
    run_embedding()
    result = run_rag_generation()

    output_path = result["rag_generation_report_path"]

    assert output_path == ROOT / "reports" / "sample" / "rag_generation_report.md"
    assert output_path.is_file()
    assert "RAG Generation Report" in output_path.read_text(encoding="utf-8")
