# Embedding and Vector Store Design

Embeddings turn text into numeric vectors that allow a retrieval system to compare a user query with document chunks. In RAG systems, this is the bridge between natural language questions and relevant source evidence.

## Deterministic Mock Embeddings

This milestone uses deterministic mock embeddings instead of external models. The same input text always produces the same vector, and different text usually produces a different vector. This keeps the project local, reproducible, lightweight, and free of paid service calls.

The mock model hashes normalized text into a configurable number of float values and normalizes the vector. It is useful for testing pipeline contracts, file formats, and retrieval flow, but it is not a semantic embedding model.

## Local Vector Artifact

The embedding runner reads `data/processed/document_chunks.json` and writes `data/processed/chunk_embeddings.json`. Each vector record preserves chunk metadata:

- `document_id`
- `chunk_id`
- `source_file`
- `chunk_index`
- `text`
- `word_count`
- `embedding`

## Cosine Similarity

Cosine similarity compares the angle between two vectors. Scores closer to `1.0` indicate vectors pointing in a more similar direction, while lower scores indicate less similarity. The local vector store embeds a query using the same mock logic, compares it with each chunk embedding, sorts by score, and returns top-ranked results.

## Future AWS Mapping

Later milestones can replace the mock model with Amazon Bedrock embedding models while keeping the same high-level interface. The local JSON vector artifact can evolve into an Amazon OpenSearch Service vector index for scalable similarity search. Amazon S3 can store source documents and processed artifacts, while ingestion and indexing can be orchestrated with AWS Lambda or AWS Step Functions.

## Limitations

- Mock embeddings are deterministic but not semantically meaningful
- Similarity scores are useful for testing, not for production relevance
- The local JSON vector store is not optimized for scale
- No Amazon Bedrock, Amazon OpenSearch Service, retrieval reranking, answer generation, or agentic workflow is implemented in this milestone
