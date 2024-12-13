import pytest
from services.vale_runner import run_vale_on_text

def test_run_vale_on_text(mocker):
    mock_subprocess = mocker.patch("subprocess.Popen")
    mock_subprocess.return_value.communicate.return_value = ('{"test": []}', "")
    mock_subprocess.return_value.returncode = 0

    result = run_vale_on_text("Sample text", "config/rules/final-template.ini")

    assert isinstance(result, dict)
    assert "test" in result
