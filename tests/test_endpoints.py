import pytest
import yaml
from fastapi.testclient import TestClient
from app.main import app
from app.services.config import Config

client = TestClient(app)

def test_get_vale_statistics():
    response = client.get("/statistics")
    assert response.status_code == 200 or response.status_code == 404
    data = response.json()
    assert "total_packages" in data
    assert "total_rules" in data
    assert "total_vocabularies" in data
    assert "rules_per_package" in data
    assert "vocab_per_category" in data

def test_search_vocabularies():
    response = client.get("/search/vocabularies?query=test")
    assert response.status_code == 200 or response.status_code == 404
    data = response.json()
    assert "results" in data

def test_search_vocabularies_with_filters():
    response = client.get("/search/vocabularies?query=test&categories=safety,efficacy&vocab_type=accept")
    assert response.status_code == 200 or response.status_code == 404
    data = response.json()
    assert "results" in data

def test_validate_vale_config():
    # Use a valid JSON config file for testing
    response = client.post("/validate/config?config_path=config/default.json")
    assert response.status_code == 200 or response.status_code == 404
    data = response.json()
    assert "is_valid" in data
    assert "errors" in data
    assert "warnings" in data

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "version": "1.0.0"}

def test_get_package_rules():
    response = client.get("/packages/CSR/rules")
    assert response.status_code == 200
    data = response.json()
    assert "package" in data
    assert "rules" in data

def test_get_category_vocabularies():
    response = client.get("/vocabularies/CSR")
    assert response.status_code == 200
    data = response.json()
    assert "vocabularies" in data

def test_validate_rule():
    rule = {
        "rule_name": "test.rule",
        "rule_content": {
            "message": "Test message",
            "level": "warning",
            "scope": "text",
            "pattern": "\\b(test)\\b"
        }
    }
    response = client.post("/rules/validate", json=rule)
    assert response.status_code == 200
    data = response.json()
    assert "is_valid" in data
    assert "errors" in data
    assert "warnings" in data

def test_export_vocabulary():
    response = client.get("/vocabularies/export/CSR?format=json")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "accept" in data or "reject" in data

def test_get_package_statistics():
    response = client.get("/packages/CSR/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_rules" in data
    assert "rules_by_severity" in data
    assert "rules_by_category" in data
    assert "active_rules" in data

def test_search_rules():
    response = client.get("/search/rules?query=test")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for rule in data:
        assert "package" in rule
        assert "rule" in rule
        assert "description" in rule
        assert "severity" in rule

@pytest.fixture
def test_rule_file(tmp_path):
    """Create a temporary test rule file."""
    from pathlib import Path
    # Create the CSR directory structure
    styles_path = tmp_path / ".vale" / "styles" / "CSR"
    styles_path.mkdir(parents=True, exist_ok=True)

    # Create initial test rule
    rule_content = {
        "message": "Test message",
        "level": "warning",
        "scope": "text",
        "pattern": "\\b(test)\\b"
    }
    rule_file = styles_path / "test_rule.yml"
    with open(rule_file, "w") as f:
        yaml.safe_dump(rule_content, f)

    # Create initial test rule
    rule_content = {
        "message": "Test message",
        "level": "warning",
        "scope": "text",
        "pattern": "\\b(test)\\b"
    }
    rule_file = styles_path / "test_rule.yml"
    with open(rule_file, "w") as f:
        yaml.safe_dump(rule_content, f)

    # Create a Config class with the test paths
    class TestConfig:
        def __init__(self):
            self.config = type("config", (), {
                "vale": {
                    "styles_path": str(tmp_path / ".vale" / "styles"),
                    "config_path": str(tmp_path / ".vale.ini")
                }
            })()

    # Override the Config dependency
    app.dependency_overrides[Config] = TestConfig

    yield rule_file

    # Cleanup
    app.dependency_overrides.clear()

def test_update_rule(test_rule_file):
    rule_content = {
        "message": "Updated test message",
        "level": "warning",
        "scope": "text",
        "pattern": "\\b(test)\\b"
    }
    response = client.put("/rules/CSR/test_rule", json=rule_content)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "message" in data

def test_update_rule_invalid_content(test_rule_file):
    rule_content = {
        "message": "Invalid rule"
        # Missing required fields
    }
    response = client.put("/rules/CSR/test_rule", json=rule_content)
    assert response.status_code == 400
    assert "Invalid rule content" in response.json()["detail"]

def test_update_vocabulary():
    terms = ["term1", "term2", "term3"]
    response = client.put("/vocabularies/test_category/accept", json=terms)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["terms_count"] == 3

def test_update_vocabulary_empty_terms():
    response = client.put("/vocabularies/test_category/reject", json=[])
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["terms_count"] == 0
