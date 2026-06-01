# Deployment Blueprint

This plan describes a phased path from the local MVP to an AWS production architecture. It does not create infrastructure and should not be read as deployed state.

## Phase 1 - Local MVP

Objective: Validate local ingestion, retrieval, mock generation, guardrails, evaluation, and monitoring.

AWS services introduced: None.

Implementation steps: run local pipelines, keep artifacts under `data/`, `outputs/`, and `reports/`, and maintain pytest coverage.

Validation checks: all tests pass, sample reports exist, and no secrets are committed.

Rollback considerations: revert local code changes and regenerate artifacts.

Cost/risk notes: no AWS cost; risk is limited to local mock behavior.

## Phase 2 - S3-Backed Document Storage

Objective: Move raw and processed document storage to Amazon S3.

AWS services introduced: Amazon S3, AWS KMS, AWS IAM.

Implementation steps: create raw and processed buckets, enable encryption, block public access, define lifecycle rules, and adapt loaders to S3 prefixes.

Validation checks: upload sample documents, verify encrypted storage, and confirm least-privilege read/write roles.

Rollback considerations: keep local document loader path available.

Cost/risk notes: low storage cost; main risk is bucket policy misconfiguration.

## Phase 3 - Bedrock Embeddings

Objective: Replace mock embeddings with Amazon Bedrock embeddings.

AWS services introduced: Amazon Bedrock.

Implementation steps: create embedding client abstraction, configure model ID, batch chunk embedding calls, and cache embeddings.

Validation checks: embedding dimensions are stable, costs are tracked, and outputs match vector index requirements.

Rollback considerations: keep mock embedding provider behind the same interface.

Cost/risk notes: embedding cost scales with corpus size and re-index frequency.

## Phase 4 - OpenSearch Vector Index

Objective: Replace local vector JSON with Amazon OpenSearch Service vector search.

AWS services introduced: Amazon OpenSearch Service.

Implementation steps: create vector index schema, write indexer, configure k-NN search, and migrate chunk metadata.

Validation checks: top-k retrieval works, latency is acceptable, and access controls are enforced.

Rollback considerations: keep local vector store for development and regression tests.

Cost/risk notes: OpenSearch can be a major fixed cost; start small and monitor utilization.

## Phase 5 - Bedrock Generation

Objective: Replace mock generation with Amazon Bedrock model invocation.

AWS services introduced: Amazon Bedrock.

Implementation steps: add model invocation client, pass assembled prompt, capture response metadata, and retain citation validation.

Validation checks: answers are grounded, citations validate, and refusal behavior is tested.

Rollback considerations: keep mock generator as local fallback.

Cost/risk notes: generation cost depends on token volume and model choice.

## Phase 6 - API Gateway + Lambda Endpoint

Objective: Expose query serving through a managed API.

AWS services introduced: Amazon API Gateway, AWS Lambda, optionally Amazon Cognito.

Implementation steps: create `/query` endpoint, authenticate requests, call query guardrails, retrieval, generation, and answer guardrails.

Validation checks: request/response schema tests, throttling, authentication, latency, and error handling.

Rollback considerations: disable API stage or route traffic back to local/manual workflows.

Cost/risk notes: API and Lambda costs scale with request volume.

## Phase 7 - Guardrails + IAM Hardening

Objective: Add managed guardrails and production access controls.

AWS services introduced: Amazon Bedrock Guardrails, AWS IAM, AWS Secrets Manager.

Implementation steps: define guardrail policies, restrict Bedrock actions, move secrets to Secrets Manager, and audit roles.

Validation checks: prompt injection tests, sensitive-data tests, invalid-citation tests, and IAM access reviews.

Rollback considerations: keep custom deterministic checks enabled if managed guardrails need tuning.

Cost/risk notes: safety misconfiguration can create enterprise risk; rollout gradually.

## Phase 8 - CloudWatch Monitoring

Objective: Add operational metrics, logs, and alarms.

AWS services introduced: Amazon CloudWatch.

Implementation steps: emit structured logs, custom metrics, dashboards, alarms, and log retention policies.

Validation checks: alarms fire on test failures, logs redact sensitive data, and metrics match local dashboard artifacts.

Rollback considerations: lower log verbosity and disable noisy alarms.

Cost/risk notes: CloudWatch log volume can grow quickly; use retention limits.

## Phase 9 - Evaluation Automation

Objective: Run scheduled quality checks.

AWS services introduced: AWS Step Functions, Amazon EventBridge, Amazon S3.

Implementation steps: schedule evaluation jobs, store results in S3, compare against thresholds, and notify on regressions.

Validation checks: scheduled runs complete, reports are generated, and failing thresholds create alerts.

Rollback considerations: pause schedule or revert to manual evaluation runner.

Cost/risk notes: evaluation model calls can become expensive if using Bedrock generation or judge models.

## Phase 10 - Dashboard/Reporting Layer

Objective: Make quality and operations visible to stakeholders.

AWS services introduced: Amazon QuickSight, Amazon OpenSearch dashboards, Amazon S3.

Implementation steps: publish metrics datasets, build dashboards, define executive and engineering views, and document interpretation.

Validation checks: dashboard refresh works, role-based access is enforced, and metrics align with reports.

Rollback considerations: continue using Markdown and CSV artifacts.

Cost/risk notes: dashboard costs depend on users, refresh frequency, and retained data volume.
