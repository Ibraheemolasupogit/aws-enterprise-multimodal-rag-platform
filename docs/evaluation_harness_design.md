# Evaluation Harness Design

RAG evaluation matters because retrieval and generation quality need to be measured before a system is trusted in production. This local harness provides deterministic checks for the current mock RAG pipeline without using LLM-as-a-judge, Amazon Bedrock, paid services, or external APIs.

## What Is Evaluated Locally

The harness evaluates sample questions from `data/evaluation/sample_questions.csv`. For each question it records retrieval behavior, citation validity, groundedness, answer completeness, insufficient-evidence handling, and basic latency metadata.

## Why Deterministic Scoring

Deterministic scoring keeps the project lightweight, reproducible, and easy to test. The rules are intentionally simple so they can later be replaced with stronger benchmarking methods or model-based evaluators.

## Retrieval Hit

`retrieval_hit` is true when the pipeline returns at least one context for a question. For the out-of-scope sample, the evaluator deliberately checks the no-context path to verify insufficient-evidence behavior.

## Keyword Coverage

Expected keywords are defined in the CSV as pipe-separated values. Keyword coverage is the fraction of expected keywords found in the retrieved context text or generated mock answer.

## Citation Validity

Citation validity uses the local citation validator. It checks that used citations exist in retrieved contexts and that answers cite available context when context exists.

## Groundedness Approximation

Groundedness is approximated through citation validity and lexical overlap between answer text and retrieved context. This is not semantic entailment, but it gives a transparent local signal.

## Future Mapping

This harness prepares the project for GenAI benchmarking, model comparison, retrieval regression testing, and production monitoring. Later versions can map to Amazon Bedrock model evaluation for managed evaluation workflows and Amazon CloudWatch for runtime metrics, logs, no-result rates, latency, and quality dashboards.

## Limitations

- No LLM-as-a-judge is used
- Keyword checks are lexical and do not understand synonyms
- Groundedness is approximate and not factual entailment
- Mock generation is deterministic and not representative of real model behavior
- Local runtime measurements are development signals, not production latency metrics
