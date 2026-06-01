from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_required_directories_exist():
    required_directories = [
        "documents/raw",
        "documents/processed",
        "documents/sample",
        "data/knowledge_base",
        "data/evaluation",
        "data/sample",
        "prompts/system_prompts",
        "prompts/rag_prompts",
        "prompts/evaluation_prompts",
        "prompts/agent_prompts",
        "config",
        "outputs/sample",
        "reports/sample",
        "docs",
        "tests",
        "src/enterprise_rag_platform",
    ]

    missing = [path for path in required_directories if not (ROOT / path).is_dir()]

    assert missing == []


def test_required_config_files_exist():
    required_config_files = [
        "config/rag_config.yaml",
        "config/model_config.yaml",
        "config/evaluation_config.yaml",
        "config/guardrails_config.yaml",
        "config/aws_architecture_mapping.yaml",
    ]

    missing = [path for path in required_config_files if not (ROOT / path).is_file()]

    assert missing == []


def test_required_package_files_exist():
    package_root = ROOT / "src" / "enterprise_rag_platform"
    subpackages = [
        "ingestion",
        "chunking",
        "embeddings",
        "retrieval",
        "generation",
        "citations",
        "guardrails",
        "evaluation",
        "recommendations",
        "agents",
        "monitoring",
        "reporting",
        "utils",
    ]

    assert (package_root / "__init__.py").is_file()
    missing = [
        package
        for package in subpackages
        if not (package_root / package / "__init__.py").is_file()
    ]

    assert missing == []


def test_required_sample_files_exist():
    required_sample_files = [
        "outputs/sample/.gitkeep",
        "reports/sample/.gitkeep",
        "documents/sample/sample_policy.md",
        "data/evaluation/sample_questions.csv",
        ".github/workflows/python-ci.yml",
    ]

    missing = [path for path in required_sample_files if not (ROOT / path).is_file()]

    assert missing == []
