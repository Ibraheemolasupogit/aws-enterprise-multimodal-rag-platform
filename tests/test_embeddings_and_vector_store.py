import json
from pathlib import Path

from enterprise_rag_platform.embeddings.embedding_model import MockEmbeddingModel
from enterprise_rag_platform.embeddings.embedding_runner import run_embedding
from enterprise_rag_platform.ingestion.ingestion_runner import load_config, run_ingestion
from enterprise_rag_platform.retrieval.retrieval_runner import run_retrieval
from enterprise_rag_platform.retrieval.vector_store import (
    LocalVectorStore,
    cosine_similarity,
)


ROOT = Path(__file__).resolve().parents[1]


def test_embedding_output_is_deterministic():
    model = MockEmbeddingModel(dimension=16)

    assert model.embed("same text") == model.embed("same text")
    assert model.embed("same text") != model.embed("different text")


def test_embedding_vector_has_configured_dimension():
    config = load_config()
    model = MockEmbeddingModel(dimension=int(config["embedding_dimension"]))

    embedding = model.embed("enterprise policy source material")

    assert len(embedding) == int(config["embedding_dimension"])
    assert all(isinstance(value, float) for value in embedding)


def test_empty_text_is_handled_safely():
    model = MockEmbeddingModel(dimension=8)

    try:
        model.embed("   ")
    except ValueError as error:
        assert "must not be empty" in str(error)
    else:
        raise AssertionError("Expected empty text to raise ValueError")


def test_chunk_embeddings_json_is_created():
    run_ingestion()
    result = run_embedding()

    output_path = result["embedding_output_path"]
    records = json.loads(output_path.read_text(encoding="utf-8"))

    assert output_path.is_file()
    assert records
    assert "embedding" in records[0]


def test_vector_store_loads_records():
    run_ingestion()
    embedding_result = run_embedding()
    config = load_config()

    vector_store = LocalVectorStore.from_json(
        embedding_result["embedding_output_path"],
        embedding_dimension=int(config["embedding_dimension"]),
    )

    assert vector_store.records


def test_cosine_similarity_returns_valid_scores():
    score = cosine_similarity([1.0, 0.0], [1.0, 0.0])

    assert score == 1.0


def test_top_k_search_returns_ranked_results():
    run_ingestion()
    embedding_result = run_embedding()
    config = load_config()
    vector_store = LocalVectorStore.from_json(
        embedding_result["embedding_output_path"],
        embedding_dimension=int(config["embedding_dimension"]),
    )

    results = vector_store.search("source material and AI responses", top_k=1)

    assert len(results) == 1
    assert results[0]["rank"] == 1
    assert results[0]["document_id"]
    assert results[0]["chunk_id"]
    assert results[0]["text"]
    assert -1.0 <= results[0]["similarity_score"] <= 1.0


def test_retrieval_output_artifact_is_created():
    run_ingestion()
    run_embedding()
    result = run_retrieval()

    output_path = result["retrieval_results_output_path"]
    records = json.loads(output_path.read_text(encoding="utf-8"))

    assert output_path == ROOT / "outputs" / "sample" / "retrieval_results.json"
    assert output_path.is_file()
    assert records
