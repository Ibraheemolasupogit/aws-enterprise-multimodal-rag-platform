from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_readme_contains_milestone_10():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "Milestone 10" in readme


def test_readme_contains_quickstart_or_example_commands():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "Quickstart" in readme
    assert "python -m enterprise_rag_platform.ingestion.ingestion_runner" in readme


def test_readme_mentions_core_project_themes():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    for phrase in [
        "local-first",
        "AWS Target Architecture",
        "evaluation",
        "guardrails",
        "monitoring",
    ]:
        assert phrase in readme


def test_portfolio_docs_exist():
    required_docs = [
        "docs/project_roadmap.md",
        "docs/interview_talking_points.md",
        "docs/example_commands.md",
        "docs/evidence_artifacts.md",
        "docs/repository_review_checklist.md",
    ]

    missing = [path for path in required_docs if not (ROOT / path).is_file()]

    assert missing == []


def test_python_ci_exists():
    assert (ROOT / ".github" / "workflows" / "python-ci.yml").is_file()
