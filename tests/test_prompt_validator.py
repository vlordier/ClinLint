import pytest
from pathlib import Path

from app.services.prompt_validator import PromptValidator
from app.schemas.prompt_schemas import (
    PromptTemplate,
    PromptVariable,
    PromptVariableType
)

@pytest.fixture
def valid_template():
    """Create a valid template for testing."""
    return {
        "name": "test_template",
        "description": "A test template",
        "template": "This is a {text} with {number}",
        "variables": {
            "text": {
                "name": "text",
                "type": "text",
                "description": "Text input",
                "required": True
            },
            "number": {
                "name": "number",
                "type": "number",
                "description": "Number input",
                "required": True
            }
        },
        "tags": ["test"],
        "version": "1.0.0"
    }

@pytest.fixture
def invalid_template():
    """Create an invalid template for testing."""
    return {
        "name": "invalid_template",
        "description": "An invalid template",
        "template": "This uses {undefined_var}",
        "variables": {},
        "version": "invalid"
    }

def test_validate_prompt_valid(valid_template):
    """Test validation of a valid template."""
    validator = PromptValidator()
    result = validator.validate_prompt(valid_template)
    assert result.is_valid
    assert not result.errors
    assert not result.warnings

def test_validate_prompt_invalid(invalid_template):
    """Test validation of an invalid template."""
    validator = PromptValidator()
    result = validator.validate_prompt(invalid_template)
    assert not result.is_valid
    assert result.errors
    assert "undefined variables" in result.errors[0]

def test_validate_prompts_batch(tmp_path):
    """Test batch validation of templates."""
    prompt_dir = tmp_path / "prompts"
    prompt_dir.mkdir()

    # Create test templates
    template1 = prompt_dir / "template1.yaml"
    template1.write_text("""
name: template1
description: Test template 1
template: Hello {name}!
variables:
  name:
    name: name
    type: text
    description: User name
    required: true
version: 1.0.0
tags: [test]
""")

    template2 = prompt_dir / "template2.yaml"
    template2.write_text("""
name: template2
description: Test template 2
template: Invalid {missing}
variables: {}
version: 1.0.0
tags: [test]
""")

    validator = PromptValidator()
    results = validator.validate_prompts_batch(prompt_dir)

    assert len(results) == 2
    assert results["template1"].is_valid
    assert not results["template2"].is_valid

def test_validate_prompt_warnings():
    """Test template validation warnings."""
    template = {
        "name": "warning_template",
        "description": "Short",  # Too short description
        "template": "A very long " + "template " * 200,  # Too long
        "variables": {
            "unused": {
                "name": "unused",
                "type": "text",
                "description": "Unused variable",
                "required": True
            }
        },
        "version": "1.0.0"
    }

    validator = PromptValidator()
    result = validator.validate_prompt(template)

    assert result.is_valid  # Warnings don't make it invalid
    assert result.warnings
    assert any("description is very short" in w for w in result.warnings)
    assert any("exceeds recommended length" in w for w in result.warnings)
    assert any("unused variables" in w for w in result.warnings)

def test_validate_prompt_variable_references():
    """Test validation of variable references."""
    template = {
        "name": "var_template",
        "description": "Template with variables",
        "template": "Using {text} and {context}",
        "variables": {
            "text": {
                "name": "text",
                "type": "text",
                "description": "Text input",
                "required": True
            }
        },
        "version": "1.0.0"
    }

    validator = PromptValidator()
    result = validator.validate_prompt(template)

    assert not result.is_valid
    assert any("undefined variables: context" in e for e in result.errors)
