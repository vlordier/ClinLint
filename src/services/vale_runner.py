import json
import logging
import subprocess
from pathlib import Path
from typing import Optional

from services.exceptions import AnalysisError, ConfigurationError
from services.vale_config_manager import ValeConfigManager

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def run_vale_on_text(
    text: str,
    config_path: Optional[str] = None,
    packages: Optional[list[str]] = None,
    styles: Optional[list[str]] = None,
) -> dict[str, list[dict[str, str | int]]]:
    """Runs Vale linting on the provided text.

    Args:
        text: Input text to lint
        config_path: Optional path to Vale configuration file
        packages: Optional list of package names to use
        styles: Optional list of style names to use

    Returns:
        Parsed Vale linting results

    Raises:
        ConfigurationError: If Vale is not found or config is invalid
        AnalysisError: If Vale execution fails
    """
    # Create temporary config if packages/styles specified
    if packages and styles:
        config_manager = ValeConfigManager()
        config_content = config_manager.create_vale_config(packages, styles)
        tmp_config = Path("tmp_vale.ini")
        tmp_config.write_text(config_content)
        config_path = str(tmp_config)
    import shutil

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
        raise AnalysisError(f"Failed to run Vale linting: {e}") from e
