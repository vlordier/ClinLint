
import json
import pytest

from services.exceptions import AnalysisError
from services.exceptions import ConfigurationError
from services.vale_runner import run_vale_on_text


@pytest.mark.parametrize("text, expected_output", [
    ("The patient showed improvement.", {"stdin.md": [{"Line": 1, "Message": "Use 'subject' instead of 'patient'", "Rule": "CSR.Terminology", "Severity": "error"}]}),
    ("The results were significant.", {"stdin.md": [{"Line": 1, "Message": "Avoid vague terms like 'significant'.", "Rule": "CSR.Vagueness", "Severity": "error"}]})
])
def test_run_vale_success(mocker, text, expected_output):
    expected_output = {
        "stdin.md": [
            {
                "Line": 1,
                "Message": "Use 'subject' instead of 'patient'",
                "Rule": "CSR.Terminology",
                "Severity": "error"
            }
        ]
    }

    mock_subprocess = mocker.patch("subprocess.Popen")
    mock_subprocess.return_value.communicate.return_value = (
        '{"stdin.md": [{"Line": 1, "Message": "Use \'subject\' instead of \'patient\'", "Rule": "CSR.Terminology", "Severity": "error"}]}',
        ""
    )
    mock_subprocess.return_value.returncode = 0

    result = run_vale_on_text("The patient showed improvement.", "config/rules/final-template.ini")

    assert result == expected_output
    mock_subprocess.assert_called_once()

def test_run_vale_empty_text(mocker):
    mock_subprocess = mocker.patch("subprocess.Popen")
    mock_subprocess.return_value.communicate.return_value = ('{}', "")
    mock_subprocess.return_value.returncode = 0

    result = run_vale_on_text("", "config/rules/final-template.ini")
    assert result == {}

@pytest.mark.parametrize("text, config_path, expected_output", [
    ("The patient showed improvement.", "config/rules/final-template.ini", {"stdin.md": [{"Line": 1, "Message": "Use 'subject' instead of 'patient'", "Rule": "CSR.Terminology", "Severity": "error"}]}),
    ("The results were significant.", "config/rules/another-template.ini", {"stdin.md": [{"Line": 1, "Message": "Avoid vague terms like 'significant'.", "Rule": "CSR.Vagueness", "Severity": "error"}]})
])
def test_run_vale_success_with_different_configs(mocker, text, config_path, expected_output):
    mock_subprocess = mocker.patch("subprocess.Popen")
    mock_subprocess.return_value.communicate.return_value = (
        json.dumps(expected_output),
        ""
    )
    mock_subprocess.return_value.returncode = 0

    result = run_vale_on_text(text, config_path)
    assert result == expected_output
    mock_subprocess.assert_called_once()

@pytest.mark.parametrize("text, error_message", [
    ("Sample text", "Vale configuration error"),
    ("Another sample", "Vale execution failed")
])
def test_run_vale_error(mocker, text, error_message):
    mock_subprocess = mocker.patch("subprocess.Popen")
    mock_subprocess.return_value.communicate.return_value = ('', "Vale configuration error")
    mock_subprocess.return_value.returncode = 1

    with pytest.raises(AnalysisError, match="Vale error: Vale configuration error"):
        run_vale_on_text("Sample text", "config/rules/final-template.ini")

def test_run_vale_missing_executable(mocker):
    mock_shutil = mocker.patch("shutil.which")
    mock_shutil.return_value = None

    with pytest.raises(ConfigurationError, match="Vale executable not found in PATH"):
        run_vale_on_text("Sample text", "config/rules/final-template.ini")

def test_run_vale_invalid_json(mocker):
    mock_subprocess = mocker.patch("subprocess.Popen")
    mock_subprocess.return_value.communicate.return_value = ('invalid json', "")
    mock_subprocess.return_value.returncode = 0

    with pytest.raises(AnalysisError):
        run_vale_on_text("Sample text", "config/rules/final-template.ini")
