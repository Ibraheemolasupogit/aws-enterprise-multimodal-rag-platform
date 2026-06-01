# Document Ingestion Design

Document ingestion turns enterprise content into structured records that downstream RAG, evaluation, guardrails, recommendations, monitoring, and agent workflows can use consistently. This milestone keeps ingestion local and deterministic so the project can be tested without AWS, paid services, credentials, or production data.

## Supported Local Formats

The local loader supports:

- Markdown files from `documents/sample/`
- Plain text files from `documents/sample/`

Each loaded document becomes a structured record with a stable `document_id`, source filename, raw text, character count, and word count.

## Preprocessing Logic

The preprocessing layer normalizes text while preserving useful document structure:

- Collapses repeated blank lines
- Normalizes spaces and tabs
- Removes obvious Markdown formatting noise such as emphasis markers and code ticks
- Keeps heading text so later retrieval can benefit from section context
- Adds cleaned character and word counts

## Chunking Logic

The chunker uses simple word-based chunks with configurable size and overlap. Each chunk preserves the originating `document_id` and `source_file`, receives a stable `chunk_id`, includes a zero-based `chunk_index`, and stores its word count.

This intentionally avoids embeddings, retrieval, reranking, or model calls. The output is a local contract for future pipeline stages.

## Outputs

Running the pipeline creates:

- `data/processed/documents.json`
- `data/processed/document_chunks.json`
- `reports/document_ingestion_report.md`

## How This Prepares for RAG

RAG systems need normalized source records and chunks before they can build indexes, generate embeddings, evaluate retrieval quality, or cite evidence. This milestone creates those records in a predictable local format so later components can focus on retrieval, generation, citations, and evaluation.

## Future AWS Mapping

In a production AWS architecture, this layer could map to:

- Amazon S3 for document storage and processed artifacts
- Amazon Textract for extracting text from PDFs, scans, and images
- Amazon Bedrock Knowledge Bases for managed ingestion and retrieval workflows
- Amazon OpenSearch Service for vector and lexical search indexes
- AWS Step Functions and AWS Lambda for ingestion orchestration
- Amazon CloudWatch for ingestion logs and monitoring

## Local Limitations

- Only Markdown and plain text files are supported
- No PDF, image, table, audio, or video extraction is implemented
- No OCR, layout analysis, embeddings, retrieval, model inference, or AWS integration is included
- Word-based chunking is simple and may split semantic units
- All sample data is mock content for local development only
