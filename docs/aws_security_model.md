# AWS Security Model

This security model describes the target AWS deployment posture for the enterprise RAG platform. It is a design document only and does not create IAM policies or AWS resources.

## IAM Roles

Use separate IAM roles for ingestion, preprocessing, embedding, indexing, query serving, evaluation, monitoring, and reporting. Each role should have a narrow trust policy and resource-scoped permissions.

## Least Privilege Policy Design

Policies should scope access to exact S3 buckets and prefixes, OpenSearch indexes, Bedrock model actions, CloudWatch log groups, and Secrets Manager secrets. Avoid wildcard actions and wildcard resources except during short-lived experiments in isolated development environments.

## S3 Bucket Security

Enable block public access, default encryption, versioning where useful, access logging, lifecycle policies, and bucket policies that deny insecure transport. Separate raw documents, processed documents, evaluation outputs, and reports.

## Encryption

Use encryption at rest for S3, OpenSearch, CloudWatch logs, and any persisted evaluation artifacts. Use TLS for data in transit through API Gateway, Lambda service calls, OpenSearch endpoints, and Bedrock invocation paths.

## OpenSearch Security

Use VPC access where appropriate, fine-grained access control, encryption at rest, node-to-node encryption, HTTPS enforcement, and index-level permissions. Restrict query-serving roles to read/search actions and indexing roles to write actions.

## Bedrock Access Control

Limit Bedrock model access to approved embedding and generation models. Separate embedding and generation permissions where possible. Record model IDs and invocation metadata for auditability.

## API Gateway Authentication

Possible options include IAM auth for internal services, Amazon Cognito for user-facing authentication, JWT authorizers for enterprise identity providers, or private API Gateway endpoints for internal-only deployments.

## Secrets Management

Store external connection strings, third-party API keys, and sensitive configuration in AWS Secrets Manager. Never commit credentials, access keys, API keys, or private tokens.

## Audit Logging

Capture query IDs, request IDs, document IDs, citation IDs, guardrail decisions, model IDs, evaluation run IDs, and error traces. Redact sensitive content from logs.

## CloudWatch Logs

Use structured JSON logs, separate log groups by workload, retention policies, metric filters, and alarms. Avoid logging full prompts or sensitive document content unless explicitly approved and protected.

## Data Retention

Apply S3 lifecycle policies and CloudWatch retention policies based on data classification. Evaluation reports and monitoring metrics should have documented retention periods.

## Sensitive-Data Handling

Use deterministic local checks initially, then add Bedrock Guardrails and enterprise data classification controls. Consider redaction before prompts are sent to models.

## Environment Separation

Maintain separate dev, test, and prod environments with separate accounts or isolated stacks, distinct buckets, indexes, KMS keys, IAM roles, API stages, and CloudWatch log groups.
