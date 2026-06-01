import json
from pathlib import Path

from enterprise_rag_platform.ingestion.document_loader import load_documents
from enterprise_rag_platform.ingestion.ingestion_runner import run_ingestion


ROOT = Path(__file__).resolve().parents[1]


def test_documents_can_be_loaded():
    documents = load_documents(ROOT / "documents" / "sample")

    assert documents
    assert documents[0]["document_id"]
    assert documents[0]["source_file"]
    assert documents[0]["raw_text"]
    assert documents[0]["character_count"] > 0
    assert documents[0]["word_count"] > 0


def test_ingestion_outputs_are_created():
    result = run_ingestion()

    documents_path = result["documents_output_path"]
    chunks_path = result["chunks_output_path"]
    report_path = result["report_output_path"]

    assert documents_path.is_file()
    assert chunks_path.is_file()
    assert report_path.is_file()


def test_chunks_are_structured_and_non_empty():
    run_ingestion()
    chunks_path = ROOT / "data" / "processed" / "document_chunks.json"
    chunks = json.loads(chunks_path.read_text(encoding="utf-8"))

    assert chunks
    for chunk in chunks:
        assert chunk["document_id"]
        assert chunk["chunk_id"]
        assert chunk["source_file"]
        assert chunk["text"].strip()
        assert chunk["word_count"] > 0


def test_processed_documents_json_is_created():
    run_ingestion()
    documents_path = ROOT / "data" / "processed" / "documents.json"
    documents = json.loads(documents_path.read_text(encoding="utf-8"))

    assert documents
    assert documents[0]["clean_text"]
    assert documents[0]["clean_character_count"] > 0
    assert documents[0]["clean_word_count"] > 0
