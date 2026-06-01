# Evidence Artifacts

These generated artifacts provide reviewer evidence for the local RAG pipeline.

| Artifact | What it proves |
| --- | --- |
| `data/processed/documents.json` | Documents were loaded and normalized into structured records |
| `data/processed/document_chunks.json` | Clean text was split into chunk records |
| `data/processed/chunk_embeddings.json` | Chunks were converted into deterministic mock embeddings |
| `outputs/sample/retrieval_results.json` | Local vector retrieval can return ranked results |
| `outputs/sample/retrieval_context.json` | Retrieval orchestration produces citation-ready context |
| `outputs/sample/rag_prompt.json` | Contexts are assembled into a structured RAG prompt |
| `outputs/sample/generated_answer.json` | Mock grounded generation and citation validation ran |
| `outputs/sample/evaluation_results.json` | Deterministic evaluation results were produced |
| `outputs/sample/evaluation_results.csv` | Evaluation metrics are available in dashboard-friendly CSV form |
| `outputs/sample/guardrail_results.json` | Query and answer guardrail decisions were captured |
| `outputs/sample/pipeline_health.json` | Pipeline health was calculated from local artifacts |
| `outputs/sample/dashboard_metrics.json` | Dashboard-ready metrics were generated |
| `outputs/sample/dashboard_metrics.csv` | Dashboard-ready metrics are available in CSV form |
| `reports/sample/document_ingestion_report.md` | Ingestion produced a human-readable report |
| `reports/sample/retrieval_report.md` | Basic retrieval produced a report |
| `reports/sample/retrieval_context_report.md` | Retrieval context generation produced a report |
| `reports/sample/rag_generation_report.md` | Mock RAG generation produced a report |
| `reports/sample/rag_evaluation_report.md` | Evaluation produced a quality report |
| `reports/sample/guardrail_report.md` | Guardrails produced a safety report |
| `reports/sample/monitoring_report.md` | Monitoring produced an executive summary |

The root-level `reports/document_ingestion_report.md` may exist from earlier milestone runs. Current portfolio evidence uses `reports/sample/document_ingestion_report.md`.
