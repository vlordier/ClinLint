import json
import logging
import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from app.services.exceptions import AnalysisError, ConfigurationError
from app.services.vale_config_manager import ValeConfigManager

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def get_default_vale_path(path_type: str = "config") -> Path:
    """Get platform-specific default Vale paths.

    Args:
        path_type: Either "config" or "styles"

    Returns:
        Platform-specific path for Vale config or styles
    """
    system = platform.system()
    if system == "Windows":
        base = os.getenv("LOCALAPPDATA", "")
        return (
            Path(base) / "vale" / (".vale.ini" if path_type == "config" else "styles")
        )
    elif system == "Darwin":
        base = Path.home() / "Library" / "Application Support" / "vale"
        return base / (".vale.ini" if path_type == "config" else "styles")
    else:  # Unix/Linux
        if path_type == "config":
            xdg_base = os.getenv("XDG_CONFIG_HOME", str(Path.home() / ".config"))
            return Path(xdg_base) / "vale" / ".vale.ini"
        else:
            xdg_base = os.getenv("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))
            return Path(xdg_base) / "vale" / "styles"


DEFAULT_STYLES_PATH = ".vale/styles"


def find_vale_binary() -> Optional[str]:
    """Find the Vale binary in PATH."""
    return shutil.which("vale")


def find_config_file(start_path: Path) -> Optional[Path]:
    """Search for .vale.ini or _vale.ini in parent directories."""
    current = start_path if start_path.is_dir() else start_path.parent
    while current != current.parent:
        for config_name in [".vale.ini", "_vale.ini"]:
            config_path = current / config_name
            if config_path.exists():
                return config_path
        current = current.parent
    return None


def run_vale_on_text(
    text: str,
    config_path: Optional[str] = None,
    packages: Optional[list[str]] = None,
    styles: Optional[list[str]] = None,
    rules: Optional[list[str]] = None,
    vocabularies: Optional[list[str]] = None,
    timeout: Optional[int] = None,
    max_issues: Optional[int] = None,
    ignore_patterns: Optional[list[str]] = None,
) -> dict[str, list[dict[str, str | int]]]:
    """Runs Vale linting on the provided text."""
    ValeConfigManager()
    config_path = _create_temp_config(config_path, packages, styles, rules, vocabularies)
    return _execute_vale(text, config_path, timeout)


def _create_temp_config(
    config_path: Optional[str],
    packages: Optional[list[str]],
    styles: Optional[list[str]],
    rules: Optional[list[str]],
    vocabularies: Optional[list[str]],
) -> Optional[str]:
    """Create a temporary Vale configuration file if needed."""
    if not (rules or vocabularies or (packages and styles)):
        return config_path

    config_content = ["StylesPath = .vale/styles", "MinAlertLevel = suggestion"]

    if vocabularies:
        vocab_names = [vocab.split("/")[1] for vocab in vocabularies]
        config_content.append(f"Vocabularies = {', '.join(vocab_names)}")

    config_content.append("\n[*]")

    if rules:
        config_content.extend(f"{rule.split('.')[0]}.{rule.split('.')[1]} = YES" for rule in rules)
    elif packages and styles:
        config_content.extend(f"{pkg}.{style} = YES" for pkg in packages for style in styles)

    if vocabularies:
        config_content.extend(f"{vocab.split('/')[0]}.{vocab.split('/')[1]} = YES" for vocab in vocabularies)

    import atexit
    import tempfile

    tmp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False)
    tmp_config.write("\n".join(config_content))
    tmp_config.close()

    atexit.register(lambda: Path(tmp_config.name).unlink(missing_ok=True))
    return tmp_config.name


def _execute_vale(text: str, config_path: Optional[str], timeout: Optional[int]) -> dict[str, list[dict[str, str | int]]]:
    """Execute Vale with the given configuration and text."""
    vale_path = shutil.which("vale")
    if not vale_path:
        logger.error("Vale executable not found in PATH")
        raise ConfigurationError("Vale executable not found in PATH")

    try:
        with subprocess.Popen(
            [vale_path, "--output=JSON", "--config", config_path, "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False,
        ) as process:
            stdout, stderr = process.communicate(input=text, timeout=timeout)
            if process.returncode != 0:
                error_msg = f"Vale error (code {process.returncode}): {stderr}"
                logging.error(error_msg)
                raise AnalysisError(error_msg)

            try:
                return json.loads(stdout)
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON from Vale: {stdout[:100]}..."
                logging.error(error_msg)
                raise AnalysisError(error_msg) from e

    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)
        raise AnalysisError(f"Vale process timed out after {timeout} seconds") from None
    except FileNotFoundError as e:
        error_msg = "Vale executable not found"
        logging.error(error_msg)
        raise ConfigurationError(error_msg) from e
    except Exception as e:
        logger.error(f"Failed to run Vale linting: {e}")
        error_msg = f"Failed to run Vale linting: {str(e)}"
        logging.exception(error_msg)
        raise AnalysisError(error_msg) from e
