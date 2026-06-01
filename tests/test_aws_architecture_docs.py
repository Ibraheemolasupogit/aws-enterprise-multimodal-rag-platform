from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_aws_architecture_documents_exist():
    required_docs = [
        "docs/aws_architecture_blueprint.md",
        "docs/aws_service_mapping.md",
        "docs/deployment_blueprint.md",
        "docs/aws_security_model.md",
        "docs/aws_cost_and_monitoring.md",
    ]

    missing = [path for path in required_docs if not (ROOT / path).is_file()]

    assert missing == []


def test_aws_architecture_mapping_yaml_exists():
    assert (ROOT / "config" / "aws_architecture_mapping.yaml").is_file()


def test_readme_contains_milestone_9():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "Milestone 9" in readme
    assert "AWS Architecture Mapping and Deployment Blueprint" in readme


def test_architecture_docs_mention_core_aws_services():
    combined_docs = "\n".join(
        [
            (ROOT / "docs" / "aws_architecture_blueprint.md").read_text(
                encoding="utf-8"
            ),
            (ROOT / "docs" / "aws_service_mapping.md").read_text(encoding="utf-8"),
            (ROOT / "docs" / "aws_security_model.md").read_text(encoding="utf-8"),
            (ROOT / "docs" / "aws_cost_and_monitoring.md").read_text(
                encoding="utf-8"
            ),
        ]
    )

    for service_name in ["Bedrock", "OpenSearch", "S3", "CloudWatch", "IAM"]:
        assert service_name in combined_docs


def test_architecture_mapping_yaml_contains_required_sections():
    mapping = yaml.safe_load(
        (ROOT / "config" / "aws_architecture_mapping.yaml").read_text(
            encoding="utf-8"
        )
    )
    required_sections = {
        "storage",
        "ingestion",
        "preprocessing",
        "chunking",
        "embeddings",
        "vector_search",
        "generation",
        "guardrails",
        "evaluation",
        "monitoring",
        "reporting",
        "api_layer",
        "orchestration",
        "security",
    }

    assert required_sections.issubset(set(mapping))
    for section in required_sections:
        assert "local_component" in mapping[section]
        assert "local_artifact" in mapping[section]
        assert "target_aws_service" in mapping[section]
        assert "production_responsibility" in mapping[section]
        assert "future_notes" in mapping[section]
