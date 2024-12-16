# config_manager.py

import configparser
from pathlib import Path
import logging

from app.services.exceptions import ConfigurationError

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages the Vale configuration file (.vale.ini)."""

    def __init__(self, config_path: Path, path_manager: PathManager):
        self.config_path = config_path
        self.path_manager = path_manager

    def create_config(self, default_content: Optional[str] = None) -> None:
        """Create a new Vale configuration file."""
        if self.config_path.exists():
            raise FileExistsError(f"Config file already exists: {self.config_path}")

        default_content = default_content or "[*]\nStylesPath = .vale/styles\nMinAlertLevel = suggestion\n"
        self.config_path.write_text(default_content)
        logger.info(f"Config file created: {self.config_path}")

    def update_config(self, section: str, settings: dict[str, str]) -> None:
        """Update an existing Vale configuration file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        config = configparser.ConfigParser()
        config.read(self.config_path)

        if section not in config:
            config.add_section(section)

        for key, value in settings.items():
            config.set(section, key, str(value))

        with self.config_path.open('w') as file:
            config.write(file)
        logger.info(f"Config file updated: {self.config_path}")

    def load_config(self) -> configparser.ConfigParser:
        """Load the Vale configuration file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        config = configparser.ConfigParser()
        config.read(self.config_path)
        logger.info(f"Config file loaded: {self.config_path}")
        return config

    def validate_config(self) -> dict[str, list[str]]:
        """Validate the Vale configuration file."""
        if not self.config_path.exists():
            raise ConfigurationError(f"Config file not found: {self.config_path}")

        try:
            config = self.load_config()

            errors = self._check_required_sections(config)
            warnings = []

            styles_path_errors, styles_path_warnings = self._validate_styles_path(config)
            errors.extend(styles_path_errors)
            warnings.extend(styles_path_warnings)

            errors.extend(self._validate_min_alert_level(config))
            warnings.extend(self._check_format_associations(config))

            return {"errors": errors, "warnings": warnings}

        except configparser.Error as e:
            raise ConfigurationError(f"Invalid config file format: {e}") from e

    def _check_required_sections(self, config: configparser.ConfigParser) -> list[str]:
        """Check required sections in the config."""
        errors = []
        if not config.has_section("*"):
            errors.append("Missing default [*] section")
        return errors

    def _validate_styles_path(self, config: configparser.ConfigParser) -> tuple[list[str], list[str]]:
        """Validate the StylesPath in the config."""
        errors = []
        warnings = []
        styles_path_config = config.get("DEFAULT", "StylesPath", fallback=None)
        if not styles_path_config:
            errors.append("StylesPath not specified")
        else:
            styles_dir = Path(styles_path_config)
            if not styles_dir.is_absolute():
                styles_dir = self.path_manager.base_path / styles_dir
            if not styles_dir.exists():
                warnings.append(f"StylesPath directory not found: {styles_dir}")
        return errors, warnings

    def _validate_min_alert_level(self, config: configparser.ConfigParser) -> list[str]:
        """Validate the MinAlertLevel in the config."""
        errors = []
        valid_levels = ["suggestion", "warning", "error"]
        level = config.get("DEFAULT", "MinAlertLevel", fallback="warning")
        if level.lower() not in valid_levels:
            errors.append(f"Invalid MinAlertLevel: {level}")
        return errors

    def _check_format_associations(self, config: configparser.ConfigParser) -> list[str]:
        """Check format associations in the config."""
        warnings = []
        if config.has_section("formats"):
            for ext, format_type in config["formats"].items():
                if format_type not in ["md", "rst", "adoc", "org", "html"]:
                    warnings.append(f"Unknown format type: {format_type} for {ext}")
        return warnings
