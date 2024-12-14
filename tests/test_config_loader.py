import json
import pytest
from pathlib import Path
from services.config_loader import ConfigLoader
from services.exceptions import ConfigurationError

@pytest.fixture
def mock_config_file(tmp_path):
    config = {
        "vale": {
            "config_path": ".vale.ini",
            "styles_path": ".vale/styles"
        },
        "llm": {
            "provider": "openai",
            "openai": {
                "api_key": "test-key",
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 500
            }
        },
        "prompt_dir": "src/services/prompts/"
    }
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config))
    return config_file

def test_config_loader_initialization(mock_config_file):
    loader = ConfigLoader(str(mock_config_file))
    assert loader.config_path == Path(mock_config_file)

def test_config_loader_missing_file():
    with pytest.raises(ConfigurationError):
        ConfigLoader("nonexistent/path/config.json")

def test_get_vale_config(mock_config_file):
    loader = ConfigLoader(str(mock_config_file))
    vale_config = loader.get_vale_config()
    assert "config_path" in vale_config
    assert "styles_path" in vale_config

def test_get_llm_config(mock_config_file):
    loader = ConfigLoader(str(mock_config_file))
    llm_config = loader.get_llm_config()
    assert "provider" in llm_config
    assert "openai" in llm_config

def test_get_prompt_dir(mock_config_file):
    loader = ConfigLoader(str(mock_config_file))
    prompt_dir = loader.get_prompt_dir()
    assert isinstance(prompt_dir, str)
    assert "prompts" in prompt_dir
