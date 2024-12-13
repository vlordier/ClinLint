import json
import logging
import subprocess

from services.exceptions import AnalysisError, ConfigurationError

logging.basicConfig(level=logging.INFO)


def run_vale_on_text(
    text: str, config_path: str
) -> dict[str, list[dict[str, str | int]]]:
    """Runs Vale linting on the provided text.

    Args:
        text (str): Input text to lint.
        config_path (str): Path to Vale configuration file.

    Returns:
        list: Parsed Vale linting results.
    """
    import shutil

    try:
        vale_path = shutil.which("vale")
        if not vale_path:
            logging.error("Vale executable not found in PATH")
            raise ConfigurationError("Vale executable not found in PATH")
        try:
            process = subprocess.Popen(
                [vale_path, "--output=JSON", "--config", config_path, "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=False,
            )
            stdout, stderr = process.communicate(input=text)
            if process.returncode != 0:
                logging.error(f"Vale error: {stderr}")
                raise AnalysisError(f"Vale error: {stderr}")
            return json.loads(stdout)
        except FileNotFoundError as e:
            logging.error("Vale executable not found.")
            raise ConfigurationError("Vale executable not found.") from e
        except json.JSONDecodeError as e:
            logging.error("Failed to parse Vale output.")
            raise AnalysisError("Invalid JSON output from Vale.") from e
    except Exception as e:
        logging.exception("An error occurred while running Vale")
        raise AnalysisError("Failed to run Vale linting") from e
