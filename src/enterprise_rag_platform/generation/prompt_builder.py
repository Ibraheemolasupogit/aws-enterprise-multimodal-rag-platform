"""Build grounded RAG prompts from retrieval context."""

from __future__ import annotations

import hashlib


DEFAULT_GENERATION_CONSTRAINTS = [
    "Answer only from the provided context.",
    "Cite sources using the provided citation labels.",
    "Say when the evidence is insufficient.",
    "Avoid unsupported claims and external facts.",
]


def build_prompt_id(query_id: str, context_ids: list[str]) -> str:
    """Create a deterministic prompt identifier."""
    seed = "|".join([query_id, *context_ids]).encode("utf-8")
    digest = hashlib.sha256(seed).hexdigest()[:16]
    return f"prompt_{digest}"


def build_context_blocks(
    contexts: list[dict[str, object]],
    max_context_blocks: int,
) -> list[dict[str, object]]:
    """Convert citation-ready contexts into prompt context blocks."""
    return [
        {
            "context_id": context["context_id"],
            "citation_label": context["citation_label"],
            "source_file": context["source_file"],
            "chunk_id": context["chunk_id"],
            "text": context["text"],
        }
        for context in contexts[:max_context_blocks]
    ]


def assemble_prompt(
    system_instruction: str,
    user_query: str,
    context_blocks: list[dict[str, object]],
    generation_constraints: list[str],
) -> str:
    """Assemble a text prompt suitable for a future RAG model call."""
    context_text = "\n\n".join(
        (
            f"Context {index}\n"
            f"Citation: {block['citation_label']}\n"
            f"Source: {block['source_file']} | Chunk: {block['chunk_id']}\n"
            f"Text: {block['text']}"
        )
        for index, block in enumerate(context_blocks, start=1)
    )
    if not context_text:
        context_text = "No retrieval context was provided."

    constraints_text = "\n".join(f"- {constraint}" for constraint in generation_constraints)

    return f"""System Instruction:
{system_instruction}

Task:
Use the provided context to answer the user query. If the context is insufficient, say so clearly.

Context:
{context_text}

Question:
{user_query}

Citation Rules:
- Use only citation labels shown in the context.
- Include citations next to claims they support.

Generation Constraints:
{constraints_text}

Output Format:
Answer:
Citations:
Limitations:
"""


def build_rag_prompt(
    query: dict[str, object],
    contexts: list[dict[str, object]],
    system_instruction: str,
    generation_constraints: list[str] | None = None,
    max_context_blocks: int = 3,
) -> dict[str, object]:
    """Build a structured RAG prompt object."""
    constraints = generation_constraints or DEFAULT_GENERATION_CONSTRAINTS
    context_blocks = build_context_blocks(contexts, max_context_blocks=max_context_blocks)
    query_id = str(query["query_id"])
    prompt_id = build_prompt_id(
        query_id,
        [str(block["context_id"]) for block in context_blocks],
    )
    user_query = str(query["normalized_query"])

    return {
        "prompt_id": prompt_id,
        "query_id": query_id,
        "system_instruction": system_instruction,
        "user_query": user_query,
        "context_blocks": context_blocks,
        "generation_constraints": constraints,
        "assembled_prompt": assemble_prompt(
            system_instruction=system_instruction,
            user_query=user_query,
            context_blocks=context_blocks,
            generation_constraints=constraints,
        ),
    }
