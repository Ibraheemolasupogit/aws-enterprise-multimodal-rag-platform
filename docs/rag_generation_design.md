# RAG Generation Design

Grounded generation means producing an answer from retrieved evidence instead of relying on unsupported model knowledge. In this project, the answer layer starts with structured local context, assembles a RAG prompt, produces a deterministic mock response, and validates citations.

## Why Mock Generation

This milestone does not call Amazon Bedrock, external LLM APIs, paid services, or AWS. The mock generator exists to prove the application contract: query, retrieval context, prompt, answer, citations, validation, and saved artifacts.

## Prompt Assembly

The prompt builder combines a processed query, citation-ready retrieval contexts, system instructions, and generation constraints. Each context block keeps the citation label, source file, chunk ID, and text so future model calls can produce grounded, citeable answers.

## Retrieved Context as Evidence

The retrieved contexts are treated as the only allowed evidence. The assembled prompt tells the future model to answer only from context, cite sources using provided labels, say when evidence is insufficient, and avoid unsupported claims.

## Citation Validation

Citation validation checks that used citations exist in retrieved context, that answers cite available context, and that unsupported citations are rejected. This reduces hallucination risk by making source support explicit and testable.

## Future AWS Mapping

Later milestones can replace the local mock generator with Amazon Bedrock model invocation while keeping the prompt and citation contracts. Bedrock Guardrails can be introduced to enforce safety policies, refusal behavior, and sensitive-data controls around generated output.

## Limitations

- The mock answer is deterministic and not intelligent
- It summarizes retrieved text mechanically
- Citation validation checks citation labels, not full factual entailment
- No Amazon Bedrock, Bedrock Guardrails, external LLM API, or production retrieval service is used
