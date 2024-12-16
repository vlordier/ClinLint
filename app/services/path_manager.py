# path_manager.py

from pathlib import Path
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class PathManager:
    """Manages and provides essential paths for Vale configuration."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_path = base_dir or Path(".vale") 
        if not self.base_path.exists():
            logger.error(f"Base path not found: {self.base_path}. Creating it.")
            self.base_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created base path: {self.base_path}")
            logger.info(f"Base path found: {self.base_path} ✅")
        self.vale_ini = self.base_path / ".vale.ini"
        self.styles_path = self.base_path / "styles"
        self.packages_path = self.base_path / "packages"
        self.vocabularies_path = self.base_path / "config" / "vocabularies"
        self.actions_path = self.base_path / "config" / "actions"

        logger.info(f"Base path: {self.base_path}")
        logger.info(f"Styles path: {self.styles_path}")
        logger.info(f"Config path: {self.vale_ini}")
        logger.info(f"Packages path: {self.packages_path}")
        logger.info(f"Vocabularies path: {self.vocabularies_path}")
        logger.info(f"Actions path: {self.actions_path}")

        self._ensure_directories()

        # Ensure packages path is a directory
        if not self.packages_path.exists():
            logger.warning(f"Packages path not found: {self.packages_path}. Creating it.")
            self.packages_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created packages directory: {self.packages_path}")
        elif self.packages_path.is_file():
            logger.warning(f"Packages path is a file: {self.packages_path}. Removing it to create a directory.")
            self.packages_path.unlink()
            self.packages_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created packages directory: {self.packages_path}")

    def _ensure_directories(self):
        """Ensure that essential directories exist."""
        directories = [
            self.styles_path,
            self.packages_path,
            self.vocabularies_path,
            self.actions_path
        ]
        for directory in directories:
            if not directory.exists():
                logger.warning(f"Directory not found: {directory}. Creating it.")
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {directory}")
