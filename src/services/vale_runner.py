import subprocess
import json

def run_vale_on_text(text: str, config_path: str) -> list:
    """
    Runs Vale linting on the provided text.
    Args:
        text (str): Input text to lint.
        config_path (str): Path to Vale configuration file.
    Returns:
        list: Parsed Vale linting results.
    """
    process = subprocess.Popen(
        ["vale", "--config", config_path, "--output=JSON", "-"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate(input=text)
    if process.returncode != 0:
        raise RuntimeError(f"Vale error: {stderr}")
    return json.loads(stdout)
