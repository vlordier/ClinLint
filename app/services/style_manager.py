# style_manager.py

from pathlib import Path
import logging
import yaml
from typing import TYPE_CHECKING

from app.services.exceptions import ConfigurationError
from app.schemas.style_schemas import Style, StyleRule

if TYPE_CHECKING:
    from app.schemas.style_schemas import Style

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

    def load_style(self, style_name: str) -> "Style":
        """Load a style and return a Style object."""
        from app.schemas.style_schemas import Style, StyleRule
        
        style_path = self.styles_path / style_name
        if not style_path.exists():
            raise FileNotFoundError(f"Style not found: {style_name}")

        rules = {}
        for rule_file in style_path.glob("*.yml"):
            try:
                with rule_file.open() as f:
                    rule_data = yaml.safe_load(f)
                    rule_name = rule_file.stem
                    rules[rule_name] = StyleRule(
                        name=rule_name,
                        description=rule_data.get("description"),
                        level=rule_data.get("level", "error"),
                        scope=rule_data.get("scope", "text"),
                        pattern=rule_data.get("pattern", ""),
                        message=rule_data.get("message", ""),
                        link=rule_data.get("link")
                    )
            except Exception as e:
                logger.error(f"Error loading rule {rule_file}: {e}")
                continue

        return Style(
            name=style_name,
            rules=rules,
            path=str(style_path)
        )

    def validate_style(self, style_name: str) -> bool:
        """Validate a style."""
        try:
            style = self.load_style(style_name)
            if not style.rules:
                logger.error(f"Style '{style_name}' has no valid rules")
                return False
            logger.info(f"Style validated: {style_name}")
            return True
        except Exception as e:
            logger.error(f"Validation failed for style {style_name}: {e}")
            return False
