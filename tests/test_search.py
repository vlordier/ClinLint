
import pytest
import yaml
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_vale_files(tmp_path):
    """Create mock Vale files for testing."""
    # Create config file
    config_dir = tmp_path / ".config/clinlint"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.json"
    config_file.write_text("""
    {
        "llm": {
            "provider": "openai",
            "openai": {
                "api_key": "test-key",
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 500
            }
        },
        "vale": {
            "config_path": "vale.ini",
            "styles_path": ".vale/styles"
        },
        "prompt_dir": "prompts/",
        "log_level": "INFO"
    }
    """)

    # Create mock rules
    rules_dir = tmp_path / ".vale/styles/test_package"
    rules_dir.mkdir(parents=True)

    rule_content = {
        "extends": "existence",
        "message": "Test rule",
        "level": "error",
        "tokens": ["test", "example"]
    }

    with open(rules_dir / "test_rule.yml", "w") as f:
        yaml.dump(rule_content, f)

    # Create mock vocabularies
    vocab_dir = tmp_path / ".vale/styles/config/vocabularies/test_category"
    vocab_dir.mkdir(parents=True)

    with open(vocab_dir / "accept.txt", "w") as f:
        f.write("test_term\nexample_term\n")

    with open(vocab_dir / "reject.txt", "w") as f:
        f.write("bad_term\nwrong_term\n")

    return tmp_path

def test_search_basic(mock_vale_files, monkeypatch):
    """Test basic search functionality."""
    config_file = mock_vale_files / ".config/clinlint/config.json"
    monkeypatch.setattr("app.main.Config.CONFIG_PATH", str(config_file))
    monkeypatch.setattr("app.services.config.Config.CONFIG_PATH", str(config_file))

    response = client.get("/search?query=test")
    response.raise_for_status()
    data = response.json()

    # Verify search found the test rule and vocabulary
    if not any(r["rule"] == "test_rule" for r in data["rules"]):
        pytest.fail("Test rule not found in search results")
    if not any(v["name"] == "accept" and "test_term" in v["terms"]
               for v in data["vocabularies"]):
        pytest.fail("Test term not found in vocabulary search results")

def test_search_with_filters(mock_vale_files, monkeypatch):
    """Test search with various filters."""
    config_file = mock_vale_files / ".config/clinlint/config.json"
    monkeypatch.setattr("app.main.Config.CONFIG_PATH", str(config_file))
    monkeypatch.setattr("app.services.config.Config.CONFIG_PATH", str(config_file))

    # Test rule filters
    response = client.get("/search?query=test&severity=error&rule_type=existence")
    response.raise_for_status()
    data = response.json()
    if not all(r["severity"] == "error" for r in data["rules"]):
        pytest.fail("Not all rules have severity 'error'")

    # Test vocabulary filters
    response = client.get("/search?query=test&vocab_type=accept&categories=test_category")
    response.raise_for_status()
    data = response.json()
    if not all(v["type"] == "accept" for v in data["vocabularies"]):
        pytest.fail("Not all vocabularies have type 'accept'")
    if not all(v["category"] == "test_category" for v in data["vocabularies"]):
        pytest.fail("Not all vocabularies belong to 'test_category'")

def test_search_similarity_threshold(mock_vale_files, monkeypatch):
    """Test fuzzy matching with different similarity thresholds."""
    monkeypatch.setattr("app.main.config.config_path", str(mock_vale_files))

    # High threshold should return fewer matches
    response = client.get("/search?query=test&min_similarity=90")
    high_threshold = response.json()
    high_matches = len(high_threshold.get("rules", [])) + len(high_threshold.get("vocabularies", []))

    # Lower threshold should return more matches
    response = client.get("/search?query=test&min_similarity=50")
    low_threshold = response.json()
    low_matches = len(low_threshold.get("rules", [])) + len(low_threshold.get("vocabularies", []))

    if low_matches < high_matches:
        pytest.fail("Low similarity threshold returned fewer matches than high threshold")

def test_search_error_handling(mock_vale_files, monkeypatch):
    """Test error handling in search endpoint."""
    monkeypatch.setattr("app.main.config.config_path", str(mock_vale_files))

    # Test invalid similarity threshold
    response = client.get("/search?query=test&min_similarity=101")
    if response.status_code != 422:
        pytest.fail("Expected status code 422 for invalid similarity threshold")

    # Test empty query
    response = client.get("/search?query=")
    if response.status_code != 422:
        pytest.fail("Expected status code 422 for empty query")

    # Test invalid category
    response = client.get("/search?query=test&categories=nonexistent")
    response.raise_for_status()
    data = response.json()
    if len(data["vocabularies"]) != 0:
        pytest.fail("Expected no vocabularies for nonexistent category")

def test_search_performance(mock_vale_files, monkeypatch):
    """Test search performance with large datasets."""
    monkeypatch.setattr("app.main.config.config_path", str(mock_vale_files))

    # Create many mock files
    rules_dir = mock_vale_files / ".vale/styles/test_package"
    for i in range(100):
        rule_content = {
            "extends": "existence",
            "message": f"Test rule {i}",
            "level": "error",
            "tokens": [f"test_{i}", f"example_{i}"]
        }
        with open(rules_dir / f"test_rule_{i}.yml", "w") as f:
            yaml.dump(rule_content, f)

    import time
    start_time = time.time()
    response = client.get("/search?query=test")
    end_time = time.time()

    response.raise_for_status()
    if end_time - start_time >= 2.0:
        pytest.fail("Search did not complete within 2 seconds")

def test_search_result_structure(mock_vale_files, monkeypatch):  # noqa: C901
    """Test the structure of search results."""
    config_file = mock_vale_files / ".config/clinlint/config.json"
    monkeypatch.setattr("app.main.Config.CONFIG_PATH", str(config_file))
    monkeypatch.setattr("app.services.config.Config.CONFIG_PATH", str(config_file))

    response = client.get("/search?query=test")
    response.raise_for_status()
    data = response.json()

    # Check required fields
    if "rules" not in data:
        pytest.fail("Missing 'rules' in response data")
    if "vocabularies" not in data:
        pytest.fail("Missing 'vocabularies' in response data")
    if "total_matches" not in data:
        pytest.fail("Missing 'total_matches' in response data")
    if "rule_matches" not in data:
        pytest.fail("Missing 'rule_matches' in response data")
    if "vocabulary_matches" not in data:
        pytest.fail("Missing 'vocabulary_matches' in response data")

    # Verify field types
    if not isinstance(data["rules"], list):
        pytest.fail("'rules' is not a list in response data")
    if not isinstance(data["vocabularies"], list):
        pytest.fail("'vocabularies' is not a list in response data")
    if not isinstance(data["total_matches"], int):
        pytest.fail("'total_matches' is not an int in response data")
    if not isinstance(data["rule_matches"], int):
        pytest.fail("'rule_matches' is not an int in response data")
    if not isinstance(data["vocabulary_matches"], int):
        pytest.fail("'vocabulary_matches' is not an int in response data")

    # Verify total matches calculation
    if data["total_matches"] != data["rule_matches"] + sum(len(v["terms"]) for v in data["vocabularies"]):
        pytest.fail("Total matches do not equal the sum of rule and vocabulary matches")

    # Check rule structure if rules exist
    if data["rules"]:
        rule = data["rules"][0]
        if not all(key in rule for key in ["package", "rule", "description", "severity"]):
            pytest.fail("Rule does not contain all required keys")

    # Check vocabulary structure if vocabularies exist
    if data["vocabularies"]:
        vocab = data["vocabularies"][0]
        if not all(key in vocab for key in ["name", "category", "terms", "type"]):
            pytest.fail("Vocabulary does not contain all required keys")

    # Verify total matches calculation
    if data["total_matches"] != data["rule_matches"] + data["vocabulary_matches"]:
        pytest.fail("Total matches do not equal the sum of rule and vocabulary matches")

    # Check rule structure
    if data["rules"]:
        rule = data["rules"][0]
        for key in ["package", "rule", "description", "severity"]:
            if key not in rule:
                pytest.fail(f"Rule is missing key: {key}")

    # Check vocabulary structure
    if data["vocabularies"]:
        vocab = data["vocabularies"][0]
        for key in ["name", "category", "terms", "type"]:
            if key not in vocab:
                pytest.fail(f"Vocabulary is missing key: {key}")
def test_search_special_characters(mock_vale_files, monkeypatch):
    """Test search with special characters."""
    config_file = mock_vale_files / ".config/clinlint/config.json"
    monkeypatch.setattr("app.main.Config.CONFIG_PATH", str(config_file))
    monkeypatch.setattr("app.services.config.Config.CONFIG_PATH", str(config_file))

    # Add a rule with special characters
    rules_dir = mock_vale_files / ".vale/styles/test_package"
    rule_content = {
        "extends": "existence",
        "message": "Test rule with special chars: @#$%",
        "level": "error",
        "tokens": ["test@example", "special#char"]
    }
    with open(rules_dir / "special_chars.yml", "w") as f:
        yaml.dump(rule_content, f)

    # Test searching with special characters
    response = client.get("/search?query=special#char")
    response.raise_for_status()
    data = response.json()
    if not any(r["rule"] == "special_chars" for r in data["rules"]):
        pytest.fail("Special characters rule not found in search results")

def test_search_case_sensitivity(mock_vale_files, monkeypatch):
    """Test case-sensitive and case-insensitive search."""
    config_file = mock_vale_files / ".config/clinlint/config.json"
    monkeypatch.setattr("app.main.Config.CONFIG_PATH", str(config_file))
    monkeypatch.setattr("app.services.config.Config.CONFIG_PATH", str(config_file))

    # Test with different cases
    response = client.get("/search?query=TEST")
    response.raise_for_status()
    upper_data = response.json()

    response = client.get("/search?query=test")
    response.raise_for_status()
    lower_data = response.json()

    # Should find same number of matches regardless of case
    if upper_data["total_matches"] != lower_data["total_matches"]:
        pytest.fail("Case sensitivity affected total matches")

def test_search_empty_results(mock_vale_files, monkeypatch):
    """Test search with no matching results."""
    config_file = mock_vale_files / ".config/clinlint/config.json"
    monkeypatch.setattr("app.main.Config.CONFIG_PATH", str(config_file))
    monkeypatch.setattr("app.services.config.Config.CONFIG_PATH", str(config_file))

    response = client.get("/search?query=nonexistentterm")
    response.raise_for_status()
    data = response.json()

    if data["total_matches"] != 0 or len(data["rules"]) != 0 or len(data["vocabularies"]) != 0 or data["rule_matches"] != 0 or data["vocabulary_matches"] != 0:
        pytest.fail("Expected no matches for nonexistent term")
