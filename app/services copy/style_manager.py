# style_manager.py

from pathlib import Path
import logging

from app.services.exceptions import ConfigurationError

logger = logging.getLogger(__name__)

class StyleManager:
    """Manages styles."""

    def __init__(self, styles_path: Path):
        self.styles_path = styles_path

    def list_styles(self) -> list[str]:
        """List available styles."""
        if not self.styles_path.exists():
            logger.warning("Styles directory not found.")
            return []
        return [
            d.name for d in self.styles_path.iterdir()
            if d.is_dir() and (d / ".vale.ini").exists()
        ]

    def validate_style(self, style_name: str) -> bool:
        """Validate a style."""
        style_path = self.styles_path / style_name
        if not style_path.exists():
            logger.error(f"Style not found: {style_name}")
            return False

        # Add additional validation logic here if needed
        # For example, check if .vale.ini exists and is valid
        vale_ini = style_path / ".vale.ini"
        if not vale_ini.exists():
            logger.error(f"Style '{style_name}' is missing .vale.ini file")
            return False

        # Optionally, attempt to load and parse .vale.ini to ensure it's valid
        config = configparser.ConfigParser()
        try:
            config.read(vale_ini)
            if not config.sections():
                logger.error(f"Style '{style_name}' has an invalid .vale.ini file")
                return False
        except configparser.Error as e:
            logger.error(f"Error parsing .vale.ini for style '{style_name}': {e}")
            return False

        logger.info(f"Style validated: {style_name}")
        return True
