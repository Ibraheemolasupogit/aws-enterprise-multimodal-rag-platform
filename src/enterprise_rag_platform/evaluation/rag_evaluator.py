"""Deterministic local RAG evaluation logic."""

from __future__ import annotations

import time

from enterprise_rag_platform.citations.citation_validator import validate_citations
from enterprise_rag_platform.generation.mock_generator import generate_mock_answer
from enterprise_rag_platform.generation.prompt_builder import (
    DEFAULT_GENERATION_CONSTRAINTS,
    build_rag_prompt,
)
from enterprise_rag_platform.ingestion.ingestion_runner import (
    DEFAULT_CONFIG_PATH,
    load_config,
)
from enterprise_rag_platform.retrieval.retrieval_orchestrator import (
    run_retrieval_orchestration,
)


def _contains_insufficient_evidence(text: str) -> bool:
    return "insufficient evidence" in text.lower()


def _combined_text(contexts: list[dict[str, object]], answer: dict[str, object]) -> str:
    context_text = " ".join(str(context["text"]) for context in contexts)
    return f"{context_text} {answer['answer_text']}".lower()


def calculate_keyword_coverage(
    expected_keywords: list[str],
    contexts: list[dict[str, object]],
    answer: dict[str, object],
) -> float:
    """Calculate expected keyword coverage over context and answer text."""
    if not expected_keywords:
        return 1.0

    searchable_text = _combined_text(contexts, answer)
    matched = [
        keyword
        for keyword in expected_keywords
        if keyword.lower() in searchable_text
    ]
    return round(len(matched) / len(expected_keywords), 4)


def calculate_groundedness_score(
    contexts: list[dict[str, object]],
    answer: dict[str, object],
    citation_validation: dict[str, object],
) -> float:
    """Approximate groundedness using citations and lexical overlap."""
    if not contexts:
        return 1.0 if _contains_insufficient_evidence(str(answer["answer_text"])) else 0.0
    if not citation_validation["is_valid"]:
        return 0.0

    answer_words = set(str(answer["answer_text"]).lower().split())
    context_words = set(" ".join(str(context["text"]) for context in contexts).lower().split())
    if not answer_words:
        return 0.0

    overlap = len(answer_words & context_words) / len(answer_words)
    return round(min(1.0, overlap), 4)


def calculate_answer_completeness_score(
    answer: dict[str, object],
    keyword_coverage_score: float,
) -> float:
    """Score answer completeness using non-empty text and keyword coverage."""
    if not str(answer["answer_text"]).strip():
        return 0.0
    return round((1.0 + keyword_coverage_score) / 2, 4)


def calculate_overall_score(
    keyword_coverage_score: float,
    groundedness_score: float,
    citation_valid: bool,
    answer_completeness_score: float,
    weights: dict[str, float],
) -> float:
    """Calculate a transparent weighted overall score."""
    citation_score = 1.0 if citation_valid else 0.0
    total_weight = sum(weights.values())
    if total_weight <= 0:
        raise ValueError("Evaluation weights must sum to more than zero")

    score = (
        keyword_coverage_score * weights["keyword"]
        + groundedness_score * weights["groundedness"]
        + citation_score * weights["citation"]
        + answer_completeness_score * weights["completeness"]
    ) / total_weight
    return round(score, 4)


def evaluate_question(
    record: dict[str, object],
    config: dict[str, object],
    config_path: str = str(DEFAULT_CONFIG_PATH),
) -> dict[str, object]:
    """Evaluate one question using deterministic local RAG scoring."""
    started_at = time.perf_counter()
    is_insufficient_category = (
        str(record["evaluation_category"]).lower() == "insufficient_evidence"
    )

    retrieval_response = run_retrieval_orchestration(
        str(record["question"]),
        config_path=config_path,
    )
    contexts = [] if is_insufficient_category else retrieval_response["contexts"]
    query = retrieval_response["query"]
    prompt = build_rag_prompt(
        query=query,
        contexts=contexts,
        system_instruction=str(config["system_instruction"]),
        generation_constraints=DEFAULT_GENERATION_CONSTRAINTS
        + [f"Answer style: {config['answer_style']}"],
        max_context_blocks=int(config["max_context_blocks"]),
    )
    answer = generate_mock_answer(prompt)
    citation_validation = validate_citations(answer, contexts)

    retrieval_hit = bool(contexts)
    keyword_coverage_score = calculate_keyword_coverage(
        list(record["expected_keywords"]),
        contexts,
        answer,
    )
    citation_valid = bool(citation_validation["is_valid"])
    groundedness_score = calculate_groundedness_score(
        contexts,
        answer,
        citation_validation,
    )
    completeness_score = calculate_answer_completeness_score(
        answer,
        keyword_coverage_score,
    )
    insufficient_evidence_handled = (
        is_insufficient_category
        and _contains_insufficient_evidence(str(answer["answer_text"]))
    )
    weights = {
        "keyword": float(config["evaluation_keyword_weight"]),
        "groundedness": float(config["evaluation_groundedness_weight"]),
        "citation": float(config["evaluation_citation_weight"]),
        "completeness": float(config["evaluation_completeness_weight"]),
    }
    overall_score = calculate_overall_score(
        keyword_coverage_score=keyword_coverage_score,
        groundedness_score=groundedness_score,
        citation_valid=citation_valid,
        answer_completeness_score=completeness_score,
        weights=weights,
    )

    return {
        "question_id": record["question_id"],
        "question": record["question"],
        "evaluation_category": record["evaluation_category"],
        "expected_keywords": record["expected_keywords"],
        "expected_source_hint": record["expected_source_hint"],
        "retrieval_hit": retrieval_hit,
        "context_count": len(contexts),
        "citation_valid": citation_valid,
        "keyword_coverage_score": keyword_coverage_score,
        "groundedness_score": groundedness_score,
        "answer_completeness_score": completeness_score,
        "insufficient_evidence_handled": insufficient_evidence_handled,
        "overall_score": overall_score,
        "latency_ms": round((time.perf_counter() - started_at) * 1000, 3),
        "answer_text": answer["answer_text"],
        "used_citations": answer["used_citations"],
        "citation_validation": citation_validation,
    }


def evaluate_records(
    records: list[dict[str, object]],
    config: dict[str, object],
    config_path: str = str(DEFAULT_CONFIG_PATH),
) -> list[dict[str, object]]:
    """Evaluate all records in a local evaluation dataset."""
    return [
        evaluate_question(record, config=config, config_path=config_path)
        for record in records
    ]
