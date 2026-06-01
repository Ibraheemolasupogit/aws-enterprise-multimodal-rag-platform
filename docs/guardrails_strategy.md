# Guardrails Strategy

Guardrails matter in enterprise RAG because the system must handle unsafe inputs, sensitive-data risks, unsupported answers, and insufficient evidence before future production deployment. This milestone implements deterministic local checks only. It does not use external moderation APIs, Amazon Bedrock Guardrails, or any paid service.

## Query-Level Guardrails

The query guardrail runs before retrieval. It normalizes the query and checks for empty or too-short input, prompt injection attempts, requests to ignore instructions, requests for secrets, sensitive personal-data requests, harmful operational requests, and simple out-of-scope enterprise knowledge patterns.

Blocking checks return a guarded refusal response before retrieval starts. Non-blocking scope warnings are recorded as notes so they can later support monitoring and analytics.

## Answer-Level Guardrails

The answer guardrail runs after mock generation and citation validation. It checks unsupported citations, missing citations when context exists, hallucination risk from invalid citations, and placeholder sensitive-data or unsafe-content patterns.

## Prompt Injection Detection

Local prompt injection detection uses transparent pattern matching for phrases such as attempts to ignore prior instructions or reveal hidden/system prompts. These rules are simple and explainable, not production-grade security.

## Sensitive-Data Risk Detection

Sensitive-data checks look for local patterns related to secrets, passwords, credentials, personal data, and private identifiers. The current version blocks obvious requests but does not perform real PII classification.

## Citation-Based Hallucination Risk

Citation validation is treated as a core hallucination-risk signal. If an answer cites sources that were not retrieved, or fails to cite retrieved context when citations are required, the answer guardrail blocks the final response.

## Insufficient-Evidence Handling

Insufficient-evidence responses are allowed when no context exists and the answer clearly states that evidence is insufficient. This supports safer behavior for out-of-scope questions.

## Future AWS Mapping

Later versions can map these checks to Amazon Bedrock Guardrails for managed safety policies, topic restrictions, sensitive-information handling, and response filtering. Guardrail events, blocked queries, invalid citations, and risk levels can also be sent to Amazon CloudWatch for monitoring, alerting, and audit dashboards.

## Local Limitations

- Pattern matching is easy to bypass
- No semantic safety classifier is used
- No real PII detection is implemented
- No Bedrock Guardrails or AWS services are called
- Citation validation checks labels, not full factual entailment
- These checks are portfolio-ready placeholders, not production-grade safety controls
