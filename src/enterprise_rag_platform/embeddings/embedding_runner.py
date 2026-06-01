"""CLI-friendly local embedding pipeline."""

from __future__ import annotations

import json
from pathlib import Path

from enterprise_rag_platform.embeddings.embedding_model import MockEmbeddingModel
from enterprise_rag_platform.ingestion.ingestion_runner import (
    DEFAULT_CONFIG_PATH,
    PROJECT_ROOT,
    load_config,
    resolve_project_path,
    save_json,
)


def load_chunks(chunks_path: Path) -> list[dict[str, object]]:
    """Load processed document chunks from JSON."""
    return json.loads(chunks_path.read_text(encoding="utf-8"))


def embed_chunks(
    chunks: list[dict[str, object]],
    embedding_dimension: int,
) -> list[dict[str, object]]:
    """Attach deterministic mock embeddings to chunk records."""
    model = MockEmbeddingModel(dimension=embedding_dimension)
    embedded_chunks = []

    for chunk in chunks:
        text = str(chunk.get("text", ""))
        embedded_chunks.append(
            {
                "document_id": chunk["document_id"],
                "chunk_id": chunk["chunk_id"],
                "source_file": chunk["source_file"],
                "chunk_index": chunk["chunk_index"],
                "text": text,
                "word_count": chunk["word_count"],
                "embedding": model.embed(text),
            }
        )

    return embedded_chunks


def run_embedding(config_path: str | Path = DEFAULT_CONFIG_PATH) -> dict[str, Path | int]:
    """Generate local embeddings for processed document chunks."""
    config = load_config(config_path)
    processed_output_dir = resolve_project_path(str(config["processed_output_dir"]))
    chunks_path = processed_output_dir / "document_chunks.json"
    embedding_output_path = resolve_project_path(str(config["embedding_output_path"]))
    embedding_dimension = int(config["embedding_dimension"])

    chunks = load_chunks(chunks_path)
    embedded_chunks = embed_chunks(chunks, embedding_dimension)
    save_json(embedded_chunks, embedding_output_path)

    return {
        "chunk_count": len(embedded_chunks),
        "embedding_dimension": embedding_dimension,
        "embedding_output_path": embedding_output_path,
    }


def main() -> None:
    """Run the local embedding pipeline and print the output location."""
    result = run_embedding()
    print(f"Embedded {result['chunk_count']} chunks.")
    print(f"Embedding dimension: {result['embedding_dimension']}")
    print(f"Chunk embeddings JSON: {result['embedding_output_path']}")


if __name__ == "__main__":
    main()
