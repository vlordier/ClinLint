"""Vale configuration management module."""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ValeConfigManager:
    """Manages Vale configuration, packages, and styles."""

    def __init__(self, styles_path: str = ".vale/styles"):
        """Initialize the Vale configuration manager.

        Args:
            styles_path: Path to Vale styles directory
        """
        self.styles_path = Path(styles_path)
        if not self.styles_path.exists():
            logger.warning(f"Styles directory not found: {styles_path}")
            self.styles_path.mkdir(parents=True, exist_ok=True)

    def list_packages(self) -> list[str]:
        """List available Vale packages.

        Returns:
            List of package names
        """
        return [d.name for d in self.styles_path.iterdir() if d.is_dir()]

    def list_styles(self, package: str) -> list[str]:
        """List available styles in a package.

        Args:
            package: Package name

        Returns:
            List of style names
        """
        package_path = self.styles_path / package
        if not package_path.exists():
            logger.warning(f"Package not found: {package}")
            return []
        return [f.stem for f in package_path.glob("**/*.yml")]

    def get_style_config(self, package: str, style: str) -> Optional[dict]:
        """Get configuration for a specific style.

        Args:
            package: Package name
            style: Style name

        Returns:
            Style configuration dict or None if not found
        """
        import yaml

        style_path = self.styles_path / package / f"{style}.yml"
        if not style_path.exists():
            logger.warning(f"Style not found: {style_path}")
            return None

        try:
            with open(style_path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading style config: {e}")
            return None

    def create_vale_config(self, packages: list[str], styles: list[str]) -> str:
        """Create a Vale configuration string.

        Args:
            packages: List of package names to include
            styles: List of style names to include

        Returns:
            Vale configuration string
        """
        config_lines = [
            "StylesPath = .vale/styles",
            "MinAlertLevel = suggestion",
            "[*]",
        ]

        for package in packages:
            for style in styles:
                if self.get_style_config(package, style):
                    config_lines.append(f"{package}.{style} = YES")

        return "\n".join(config_lines)
