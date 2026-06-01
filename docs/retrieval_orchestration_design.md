# Retrieval Orchestration Design

Retrieval orchestration turns a user query into structured evidence that a future RAG generator can use safely. Vector search finds potentially relevant chunks, but orchestration validates the query, applies retrieval parameters, filters results, and formats the evidence into citation-ready context records.

## Vector Search vs Retrieval Orchestration

Vector search compares a query embedding with stored chunk embeddings and returns ranked matches. Retrieval orchestration wraps that lower-level search with application behavior: query validation, top-k settings, score thresholding, response structure, and citation metadata.

## Query Validation

The query processor normalizes whitespace, rejects empty queries, enforces a configurable minimum word count, and creates a deterministic `query_id` from the normalized query. This gives later evaluation, monitoring, and reporting steps a stable query record.

## Top-K Search

The orchestrator loads the local vector store from `data/processed/chunk_embeddings.json`, embeds the normalized query with the same deterministic mock model, and retrieves the configured top-k results.

## Similarity Thresholding

After top-k search, results are filtered by `minimum_similarity_score`. In this local mock setup, the default threshold is permissive because mock embeddings are not semantically meaningful. Later semantic embeddings can use a more realistic threshold.

## Citation-Ready Contexts

Retrieved chunks are converted into context records containing source identifiers, rank, chunk text, score, a human-readable citation label, and structured citation metadata. These records are evidence only. This milestone does not generate final LLM answers.

## Future AWS Mapping

In a production AWS design, this orchestration layer could call Amazon OpenSearch Service for vector retrieval or Amazon Bedrock Knowledge Bases for managed retrieval. AWS Lambda can host the orchestration logic, Amazon API Gateway can expose query endpoints, and Amazon CloudWatch can capture logs, metrics, and no-result events.

## Local Limitations

- Mock embeddings are deterministic but not semantically meaningful
- Similarity scores are not production-quality relevance scores
- Local JSON search is not scalable
- No reranking, access control filtering, Bedrock generation, OpenSearch integration, or final answer generation is implemented
