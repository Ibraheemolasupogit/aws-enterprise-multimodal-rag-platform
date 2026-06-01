# Interview Talking Points

## 30-Second Pitch

This is a local-first enterprise RAG platform that demonstrates the full shape of an AWS GenAI system without using paid services. It covers ingestion, chunking, mock embeddings, vector retrieval, citation-ready context, mock grounded generation, citation validation, deterministic evaluation, guardrails, monitoring, and AWS architecture mapping.

## 2-Minute Technical Explanation

The project starts with local sample enterprise documents, normalizes them, chunks them, and creates deterministic mock embeddings. A local vector store performs cosine similarity search and returns citation-ready context. The generation layer assembles a RAG prompt and produces a clearly labelled mock answer using only retrieved context. Citations are validated, guardrails check both queries and answers, evaluation scores the pipeline deterministically, and monitoring produces dashboard-ready artifacts. The AWS docs map the same architecture to S3, Bedrock, OpenSearch, Lambda, API Gateway, Step Functions, CloudWatch, IAM, and Bedrock Guardrails.

## Architecture Explanation

The architecture separates ingestion, preprocessing, chunking, embeddings, retrieval, generation, citations, guardrails, evaluation, monitoring, and reporting. Each layer has a local implementation and a future AWS target. This makes the project easy to test locally and easy to discuss as a production design.

## RAG Pipeline Explanation

The local RAG flow is:

```text
document -> clean text -> chunks -> mock embeddings -> vector search -> citation context -> prompt -> mock answer -> citation validation
```

The generated answer is not from a real LLM. It is deterministic so the pipeline contract can be tested.

## Evaluation Explanation

The evaluation harness loads sample questions from CSV and scores retrieval hit, keyword coverage, citation validity, approximate groundedness, answer completeness, insufficient-evidence handling, and overall score. It is intentionally deterministic and not LLM-as-a-judge.

## Guardrails Explanation

The guardrails layer checks unsafe queries before retrieval and checks generated answers after citation validation. It detects prompt injection patterns, secrets requests, sensitive-data request patterns, unsupported citations, and missing citations.

## AWS Mapping Explanation

Local documents map to S3, mock embeddings map to Bedrock embeddings, local vector search maps to OpenSearch or Bedrock Knowledge Bases, mock generation maps to Bedrock, local guardrails map to Bedrock Guardrails plus custom Lambda checks, and local monitoring maps to CloudWatch.

## Trade-Offs

- Deterministic mocks make the system reproducible but not intelligent
- Lexical evaluation is transparent but not semantic
- JSON artifacts are simple but not scalable
- Local guardrails are explainable but not production-grade
- Documentation is blueprint-ready, while infrastructure code is intentionally deferred

## Limitations

The project is not deployed, does not call Bedrock, does not use OpenSearch, does not include Terraform/CDK, and does not process production data. It is a local MVP plus architecture blueprint.

## Role Alignment

- Data Scientist: evaluation design, metrics, experimentation readiness
- AI Engineer: modular RAG pipeline and generation contracts
- GenAI Engineer: prompt assembly, citations, guardrails, Bedrock mapping
- LLMOps Engineer: monitoring, reports, CI, quality artifacts
- AWS Engineer: service mapping, security model, deployment blueprint
