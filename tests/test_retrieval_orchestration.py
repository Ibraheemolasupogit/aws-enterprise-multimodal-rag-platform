import json
from pathlib import Path

import yaml

from enterprise_rag_platform.embeddings.embedding_runner import run_embedding
from enterprise_rag_platform.ingestion.ingestion_runner import load_config, run_ingestion
from enterprise_rag_platform.retrieval.context_builder import build_contexts
from enterprise_rag_platform.retrieval.query_processor import process_query
from enterprise_rag_platform.retrieval.retrieval_orchestrator import (
    run_retrieval_orchestration,
)
from enterprise_rag_platform.retrieval.retrieval_runner import run_retrieval


ROOT = Path(__file__).resolve().parents[1]


def test_valid_query_is_normalized():
    query = process_query("  What   does   the policy say?  ", minimum_query_words=3)

    assert query["normalized_query"] == "What does the policy say?"
    assert query["character_count"] == len("What does the policy say?")
    assert query["word_count"] == 5


def test_empty_query_is_rejected():
    try:
        process_query("   ", minimum_query_words=2)
    except ValueError as error:
        assert "must not be empty" in str(error)
    else:
        raise AssertionError("Expected empty query to raise ValueError")


def test_too_short_query_is_rejected():
    try:
        process_query("policy", minimum_query_words=2)
    except ValueError as error:
        assert "at least 2 words" in str(error)
    else:
        raise AssertionError("Expected too-short query to raise ValueError")


def test_query_id_is_deterministic():
    first = process_query("What does the policy say?", minimum_query_words=3)
    second = process_query("What   does the policy say?", minimum_query_words=3)

    assert first["query_id"] == second["query_id"]


def test_context_builder_creates_citation_fields():
    query = process_query("What does the policy say?", minimum_query_words=3)
    results = [
        {
            "rank": 1,
            "document_id": "sample_policy",
            "chunk_id": "sample_policy_chunk_0000",
            "source_file": "sample_policy.md",
            "chunk_index": 0,
            "text": "Policy text.",
            "similarity_score": 0.42,
        }
    ]

    contexts = build_contexts(query, results)

    assert contexts[0]["citation_label"] == (
        "[sample_policy.md | sample_policy_chunk_0000]"
    )
    assert contexts[0]["citation_metadata"] == {
        "document_id": "sample_policy",
        "chunk_id": "sample_policy_chunk_0000",
        "source_file": "sample_policy.md",
        "rank": 1,
        "similarity_score": 0.42,
    }


def test_retrieval_orchestrator_returns_structured_response():
    run_ingestion()
    run_embedding()

    response = run_retrieval_orchestration(
        "How should AI-generated responses handle source material?"
    )

    assert response["query"]["query_id"]
    assert response["retrieval_parameters"]["top_k"] > 0
    assert response["result_count"] == len(response["contexts"])
    assert response["contexts"]


def test_minimum_similarity_filtering_works(tmp_path):
    run_ingestion()
    run_embedding()
    config = load_config()
    config["minimum_similarity_score"] = 2.0

    config_path = tmp_path / "rag_config.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    response = run_retrieval_orchestration(
        "How should AI-generated responses handle source material?",
        config_path=config_path,
    )

    assert response["result_count"] == 0
    assert response["contexts"] == []
    assert response["no_result_reason"]


def test_retrieval_context_json_is_created():
    run_ingestion()
    run_embedding()
    result = run_retrieval()

    output_path = result["retrieval_context_output_path"]
    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert output_path == ROOT / "outputs" / "sample" / "retrieval_context.json"
    assert output_path.is_file()
    assert payload["query"]["query_id"]
    assert "contexts" in payload


def test_no_empty_context_text_is_returned():
    run_ingestion()
    run_embedding()
    response = run_retrieval_orchestration(
        "How should AI-generated responses handle source material?"
    )

    assert response["contexts"]
    assert all(context["text"].strip() for context in response["contexts"])
