# Project Roadmap

## Completed Milestones

| Milestone | Outcome |
| --- | --- |
| 1 | Repository foundation, package skeleton, CI, sample docs |
| 2 | Local document ingestion, preprocessing, chunking |
| 3 | Deterministic mock embeddings and local vector store |
| 4 | Retrieval orchestration and citation-ready context builder |
| 5 | Prompt assembly, mock RAG generation, citation validation |
| 6 | Deterministic RAG evaluation harness |
| 7 | Local query and answer guardrails |
| 8 | Monitoring, reporting, dashboard-ready artifacts |
| 9 | AWS architecture mapping and deployment blueprint |
| 10 | Portfolio polish and repository readiness |

## Future Enhancements

- Add real provider interfaces while keeping mock implementations for tests
- Add richer sample documents and evaluation datasets
- Add regression comparison across retrieval and prompt versions
- Add source-level citation spans and page/section metadata
- Add lightweight API or demo after backend contracts stabilize

## AWS Deployment Phases

1. S3-backed document storage
2. Bedrock embeddings
3. OpenSearch vector index
4. Bedrock generation
5. API Gateway and Lambda query endpoint
6. Bedrock Guardrails and IAM hardening
7. CloudWatch monitoring
8. Evaluation automation
9. Dashboard and reporting layer

## Potential Bedrock Integration

Add a Bedrock embedding provider and generation provider behind the current local interfaces. Keep deterministic mocks as the default test path.

## Potential OpenSearch Migration

Replace `chunk_embeddings.json` with an OpenSearch vector index adapter. Preserve the current retrieval result schema so downstream prompt, citation, evaluation, and monitoring code remains stable.

## Potential Streamlit or API Demo

Add a small Streamlit demo or API Gateway/Lambda-style local API once backend behavior is stable. The first demo should show query, contexts, generated answer, citations, guardrail decision, and evaluation metadata.

## CI/CD Improvements

- Add linting and formatting checks
- Add coverage reporting
- Add artifact validation tests
- Add scheduled local evaluation workflow in CI

## Multimodal Extensions

- Add Textract-style extraction placeholders for scanned PDFs and forms
- Capture image/page metadata for document chunks
- Prepare prompt/context contracts for future multimodal Bedrock models

## Experimentation and Recommender Layers

- Add A/B testing metadata for retrieval and prompt variants
- Add offline experiment summaries
- Add recommendation placeholders using document metadata, user feedback, or entity relationships

## Agentic Workflow Layer

Future agents could monitor failed evaluations, summarize guardrail trends, propose re-indexing, or triage ingestion failures. This should come after observability and API boundaries are stable.
