# package_manager.py

import zipfile
from pathlib import Path
import logging
from typing import Any, Optional

from app.services.exceptions import ConfigurationError

logger = logging.getLogger(__name__)

class PackageManager:
    """Manages Vale packages."""

    def __init__(self, packages_path: Path):
        self.packages_path = packages_path

    def list_packages(self) -> list[str]:
        """List available Vale packages."""
        if not self.packages_path.exists():
            logger.warning("Packages directory not found.")
            return []
        return [d.name for d in self.packages_path.iterdir() if d.is_dir() or d.suffix == ".zip"]

    def create_package(self, package_name: str, config_content: str, styles_dir: Optional[Path] = None) -> None:
        """Create a new package."""
        package_path = self.packages_path / f"{package_name}.zip"
        if package_path.exists():
            raise FileExistsError(f"Package already exists: {package_name}")

        with zipfile.ZipFile(package_path, 'w') as zipf:
            # Add .vale.ini file
            zipf.writestr(f"{package_name}/.vale.ini", config_content)

            # Add styles directory if provided
            if styles_dir and styles_dir.exists():
                for file in styles_dir.rglob('*'):
                    zipf.write(file, arcname=f"{package_name}/styles/{file.relative_to(styles_dir)}")

        logger.info(f"Package created: {package_name}")

    def update_package(self, package_name: str, config_content: Optional[str] = None, styles_dir: Optional[Path] = None) -> None:
        """Update an existing package."""
        package_path = self.packages_path / f"{package_name}.zip"
        if not package_path.exists():
            raise FileNotFoundError(f"Package not found: {package_name}")

        with zipfile.ZipFile(package_path, 'a') as zipf:
            # Update .vale.ini file if new content is provided
            if config_content:
                zipf.writestr(f"{package_name}/.vale.ini", config_content)

            # Update styles directory if provided
            if styles_dir and styles_dir.exists():
                for file in styles_dir.rglob('*'):
                    zipf.write(file, arcname=f"{package_name}/styles/{file.relative_to(styles_dir)}")

        logger.info(f"Package updated: {package_name}")

    def delete_package(self, package_name: str) -> None:
        """Delete a package."""
        package_path = self.packages_path / f"{package_name}.zip"
        if not package_path.exists():
            raise FileNotFoundError(f"Package not found: {package_name}")

        package_path.unlink()
        logger.info(f"Package deleted: {package_name}")

    def load_package(self, package_name: str) -> dict[str, Any]:
        """Load a package."""
        package_path = self.packages_path / f"{package_name}.zip"
        if not package_path.exists():
            raise FileNotFoundError(f"Package not found: {package_name}")

        with zipfile.ZipFile(package_path, 'r') as zipf:
            package_contents = {name: zipf.read(name).decode('utf-8') for name in zipf.namelist()}

        logger.info(f"Package loaded: {package_name}")
        return package_contents

    def validate_package(self, package_name: str) -> bool:
        """Validate a package."""
        try:
            package_contents = self.load_package(package_name)
            # Check for required files
            if f"{package_name}/.vale.ini" not in package_contents:
                logger.error(f"Package {package_name} is missing .vale.ini file")
                return False
            logger.info(f"Package validated: {package_name}")
            return True
        except Exception as e:
            logger.error(f"Validation failed for package {package_name}: {e}")
            return False
