
import pytest

from services.vale_runner import run_vale_on_text


def test_run_vale_success(mocker):
    expected_output = {
        "stdin.md": [
            {
                "Line": 1,
                "Message": "Use 'subject' instead of 'patient'",
                "Rule": "CSR.Terminology"
            }
        ]
    }

    mock_subprocess = mocker.patch("subprocess.Popen")
    mock_subprocess.return_value.communicate.return_value = (
        '{"stdin.md": [{"Line": 1, "Message": "Use \'subject\' instead of \'patient\'", "Rule": "CSR.Terminology"}]}',
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

def test_run_vale_error(mocker):
    mock_subprocess = mocker.patch("subprocess.Popen")
    mock_subprocess.return_value.communicate.return_value = ('', "Vale configuration error")
    mock_subprocess.return_value.returncode = 1

    with pytest.raises(RuntimeError) as exc_info:
        run_vale_on_text("Sample text", "config/rules/final-template.ini")
    assert "Vale error" in str(exc_info.value)

def test_run_vale_invalid_json(mocker):
    mock_subprocess = mocker.patch("subprocess.Popen")
    mock_subprocess.return_value.communicate.return_value = ('invalid json', "")
    mock_subprocess.return_value.returncode = 0

    with pytest.raises(ValueError):
        run_vale_on_text("Sample text", "config/rules/final-template.ini")
