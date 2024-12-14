import json
import pytest
import yaml
from pathlib import Path

@pytest.fixture
def mock_llm_config():
    return {
        "provider": "openai",
        "openai": {
            "api_key": "test-key",
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 500
        }
    }

@pytest.fixture
def mock_vale_config():
    return {
        "config_path": ".vale.ini",
        "styles_path": ".vale/styles"
    }

@pytest.fixture
def sample_texts():
    return [
        "The patient showed significant improvement.",
        "Approximately 50% of subjects responded.",
        "The results were statistically significant (p<0.05).",
        "The study drug was well-tolerated.",
        "Multiple adverse events were observed.",
        "The efficacy endpoint was met.",
        "Safety data indicated no concerns.",
        "Baseline characteristics were balanced."
    ]

@pytest.fixture
def mock_llm_judge():
    from services.llm_judge import LLMJudge

    class MockLLMJudge(LLMJudge):
        def __init__(self):
            pass

        def get_feedback(self, prompt_template, **kwargs):
            text = kwargs.get('text', '').lower()
            if "significant" in text:
                return {"feedback": ["Replace 'significant' with specific metrics"]}
            elif "approximately" in text:
                return {"feedback": ["State exact percentage"]}
            elif "patient" in text:
                return {"feedback": ["Use 'subject' instead of 'patient'"]}
            elif "well-tolerated" in text:
                return {"feedback": ["Provide specific safety metrics"]}
            elif "multiple" in text:
                return {"feedback": ["Specify the number of events"]}
            elif "endpoint" in text:
                return {"feedback": ["Define the specific endpoint"]}
            return {"feedback": ["Improve clarity and precision"]}

    return MockLLMJudge()

@pytest.fixture
def mock_vale_results():
    return {
        "stdin.md": [
            {
                "Line": 1,
                "Message": "Use 'subject' instead of 'patient'",
                "Rule": "CSR.Terminology"
            },
            {
                "Line": 2,
                "Message": "Avoid vague terms",
                "Rule": "CSR.Precision"
            }
        ]
    }

@pytest.fixture
def test_config_file(tmp_path):
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
