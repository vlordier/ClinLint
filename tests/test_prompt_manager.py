import pytest
import yaml
from pathlib import Path

from app.services.prompt_manager import PromptManager
from app.schemas.prompt_schemas import PromptTemplate

@pytest.fixture
def mock_prompt_dir(tmp_path):
    prompt_dir = tmp_path / "prompts"
    prompt_dir.mkdir()

    template = {
        "name": "test_template",
        "description": "A test template",
        "template": "Analyze the following text: {text}",
        "variables": {
            "text": {
                "name": "text",
                "type": "text",
                "description": "Input text",
                "required": True
            }
        },
        "tags": ["test"],
        "version": "1.0.0"
    }

    template_file = prompt_dir / "test_template.yaml"
    template_file.write_text(yaml.dump(template))
    return prompt_dir

def test_prompt_manager_initialization(mock_prompt_dir: Path) -> None:
    manager = PromptManager(str(mock_prompt_dir))
    assert manager.prompt_dir == Path(mock_prompt_dir)
    assert isinstance(manager._templates, dict)
    assert "test_template" in manager._templates

def test_get_prompt_template(mock_prompt_dir):
    manager = PromptManager(str(mock_prompt_dir))
    template = manager.get_prompt_template("test_template")
    assert isinstance(template, PromptTemplate)
    assert template.name == "test_template"
    assert "text" in template.variables

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
    assert not manager.validate_template("invalid")

def test_list_templates(mock_prompt_dir):
    manager = PromptManager(str(mock_prompt_dir))
    templates = manager.list_templates()
    assert isinstance(templates, dict)
    assert "test_template" in templates
    assert isinstance(templates["test_template"], PromptTemplate)

def test_validate_template(mock_prompt_dir):
    manager = PromptManager(str(mock_prompt_dir))
    assert manager.validate_template("test_template")
    assert not manager.validate_template("nonexistent")

def test_template_caching(mock_prompt_dir):
    manager = PromptManager(str(mock_prompt_dir))
    template1 = manager.get_prompt_template("test_template")
    template2 = manager.get_prompt_template("test_template")
    assert template1 is template2  # Should be the same instance due to caching
def test_load_all_templates(mock_prompt_dir):
    manager = PromptManager(str(mock_prompt_dir))
    assert "test_template" in manager._templates
    assert isinstance(manager._templates["test_template"], PromptTemplate)
