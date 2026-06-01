"""CLI-friendly local document ingestion pipeline."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

from enterprise_rag_platform.ingestion.document_loader import load_documents
from enterprise_rag_platform.preprocessing.document_chunker import chunk_documents
from enterprise_rag_platform.preprocessing.text_preprocessor import preprocess_documents


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "rag_config.yaml"


def load_config(config_path: str | Path = DEFAULT_CONFIG_PATH) -> dict[str, object]:
    """Load local RAG ingestion configuration."""
    with Path(config_path).open("r", encoding="utf-8") as config_file:
        return yaml.safe_load(config_file) or {}


def resolve_project_path(path_value: str | Path) -> Path:
    """Resolve config paths relative to the project root."""
    path = Path(path_value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def save_json(records: list[dict[str, object]], output_path: Path) -> None:
    """Save structured records as pretty-printed JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(records, indent=2), encoding="utf-8")


def write_report(
    output_path: Path,
    documents: list[dict[str, object]],
    chunks: list[dict[str, object]],
) -> None:
    """Write a lightweight local ingestion report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    total_raw_words = sum(int(document["word_count"]) for document in documents)
    total_clean_words = sum(int(document["clean_word_count"]) for document in documents)
    total_chunk_words = sum(int(chunk["word_count"]) for chunk in chunks)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    report = f"""# Document Ingestion Report

Generated at: {generated_at}

## Summary

- Documents processed: {len(documents)}
- Chunks created: {len(chunks)}
- Total raw words: {total_raw_words}
- Total clean words: {total_clean_words}
- Total chunk words: {total_chunk_words}

## Documents

"""

    for document in documents:
        report += (
            f"- `{document['source_file']}`: "
            f"{document['clean_word_count']} clean words, "
            f"{document['clean_character_count']} clean characters\n"
        )

    output_path.write_text(report, encoding="utf-8")


def run_ingestion(config_path: str | Path = DEFAULT_CONFIG_PATH) -> dict[str, Path | int]:
    """Run local document loading, preprocessing, chunking, and output writing."""
    config = load_config(config_path)
    input_document_dir = resolve_project_path(str(config["input_document_dir"]))
    processed_output_dir = resolve_project_path(str(config["processed_output_dir"]))
    chunk_size_words = int(config["chunk_size_words"])
    chunk_overlap_words = int(config["chunk_overlap_words"])

    documents = load_documents(input_document_dir)
    processed_documents = preprocess_documents(documents)
    chunks = chunk_documents(processed_documents, chunk_size_words, chunk_overlap_words)

    documents_output_path = processed_output_dir / "documents.json"
    chunks_output_path = processed_output_dir / "document_chunks.json"
    report_output_path = PROJECT_ROOT / "reports" / "document_ingestion_report.md"

    save_json(processed_documents, documents_output_path)
    save_json(chunks, chunks_output_path)
    write_report(report_output_path, processed_documents, chunks)

    return {
        "document_count": len(processed_documents),
        "chunk_count": len(chunks),
        "documents_output_path": documents_output_path,
        "chunks_output_path": chunks_output_path,
        "report_output_path": report_output_path,
    }


def main() -> None:
    """Run the ingestion pipeline and print output locations."""
    result = run_ingestion()
    print(f"Processed {result['document_count']} documents.")
    print(f"Created {result['chunk_count']} chunks.")
    print(f"Documents JSON: {result['documents_output_path']}")
    print(f"Chunks JSON: {result['chunks_output_path']}")
    print(f"Report: {result['report_output_path']}")


if __name__ == "__main__":
    main()
