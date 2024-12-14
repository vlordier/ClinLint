import pytest
import yaml
from pathlib import Path
from services.prompt_manager import PromptManager

@pytest.fixture
def mock_prompt_dir(tmp_path):
    prompt_dir = tmp_path / "prompts"
    prompt_dir.mkdir()
    template = {
        "template": "Analyze the following text: {text}",
        "variables": ["text"]
    }
    template_file = prompt_dir / "test_template.yaml"
    template_file.write_text(yaml.dump(template))
    return prompt_dir

def test_prompt_manager_initialization(mock_prompt_dir: Path) -> None:
    manager = PromptManager(str(mock_prompt_dir))
    assert manager.prompt_dir == Path(mock_prompt_dir)

def test_get_prompt_template(mock_prompt_dir):
    manager = PromptManager(str(mock_prompt_dir))
    template = manager.get_prompt_template("test_template")
    assert "template" in template
    assert "variables" in template

def test_get_template_content(mock_prompt_dir):
    manager = PromptManager(str(mock_prompt_dir))
    content = manager.get_template_content("test_template")
    assert isinstance(content, str)
    assert "Analyze the following text:" in content

def test_nonexistent_template(mock_prompt_dir):
    manager = PromptManager(str(mock_prompt_dir))
    with pytest.raises(FileNotFoundError):
        manager.get_prompt_template("nonexistent")

def test_invalid_yaml_template(mock_prompt_dir):
    invalid_template = mock_prompt_dir / "invalid.yaml"
    invalid_template.write_text("invalid: yaml: content")
    manager = PromptManager(str(mock_prompt_dir))
    with pytest.raises(ValueError):
        manager.get_prompt_template("invalid")
