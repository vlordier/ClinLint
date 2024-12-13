import json
import subprocess


def run_vale_on_text(text: str, config_path: str) -> dict[str, list[dict[str, str | int]]]:
    """Runs Vale linting on the provided text.

    Args:
        text (str): Input text to lint.
        config_path (str): Path to Vale configuration file.

    Returns:
        list: Parsed Vale linting results.
    """
    import shutil
    vale_path = shutil.which("vale")
    if not vale_path:
        raise RuntimeError("Vale executable not found in PATH")

    process = subprocess.Popen( # noqa
        [vale_path, "--config", config_path, "--output=JSON", "-"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=False
    )
    stdout, stderr = process.communicate(input=text)
    if process.returncode != 0:
        raise RuntimeError(f"Vale error: {stderr}")
    return json.loads(stdout)
