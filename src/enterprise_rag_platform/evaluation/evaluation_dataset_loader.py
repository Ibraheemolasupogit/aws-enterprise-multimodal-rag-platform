"""Load local RAG evaluation datasets."""

from __future__ import annotations

import csv
from pathlib import Path


REQUIRED_COLUMNS = {
    "question_id",
    "question",
    "expected_keywords",
    "expected_source_hint",
    "evaluation_category",
}


def parse_keywords(value: str) -> list[str]:
    """Parse pipe-separated expected keywords."""
    return [keyword.strip().lower() for keyword in value.split("|") if keyword.strip()]


def validate_columns(fieldnames: list[str] | None) -> None:
    """Validate that the evaluation CSV includes required columns."""
    if fieldnames is None:
        raise ValueError("Evaluation dataset is missing a header row")

    missing_columns = sorted(REQUIRED_COLUMNS - set(fieldnames))
    if missing_columns:
        raise ValueError(f"Evaluation dataset is missing columns: {missing_columns}")


def load_evaluation_dataset(dataset_path: str | Path) -> list[dict[str, object]]:
    """Load and validate local evaluation questions."""
    path = Path(dataset_path)
    records = []

    with path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        validate_columns(reader.fieldnames)

        for row in reader:
            question = str(row["question"]).strip()
            if not question:
                raise ValueError("Evaluation dataset contains an empty question")

            records.append(
                {
                    "question_id": str(row["question_id"]).strip(),
                    "question": question,
                    "expected_keywords": parse_keywords(str(row["expected_keywords"])),
                    "expected_source_hint": str(row["expected_source_hint"]).strip(),
                    "evaluation_category": str(row["evaluation_category"]).strip(),
                }
            )

    return records
