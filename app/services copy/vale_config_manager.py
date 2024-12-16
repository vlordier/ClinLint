# vale_config_manager.py

import logging
from pathlib import Path

from app.services.exceptions import ConfigurationError
from app.services.path_manager import PathManager
from app.services.vale_config_manager import ConfigManager
from app.services.package_manager import PackageManager
from app.services.vocabulary_manager import VocabularyManager
from app.services.action_manager import ActionManager
from app.services.style_manager import StyleManager

logger = logging.getLogger(__name__)

class ValeConfigManager:
    """Orchestrates various managers to handle Vale configuration."""

    def __init__(self):
        """Initialize the Vale configuration manager."""
        self.path_manager = PathManager()
        self.config_manager = ConfigManager(self.path_manager.vale_ini, self.path_manager)
        self.package_manager = PackageManager(self.path_manager.packages_path)
        self.vocabulary_manager = VocabularyManager(self.path_manager.vocabularies_path)
        self.action_manager = ActionManager(self.path_manager.actions_path)
        self.style_manager = StyleManager(self.path_manager.styles_path)

        logger.info("ValeConfigManager initialized successfully.")

        if not self._check_vale_installation():
            raise ConfigurationError("Vale is not installed or not in PATH")

    def _check_vale_installation(self) -> bool:
        """Check if Vale is installed and accessible."""
        from services.vale_runner import find_vale_binary

        return find_vale_binary() is not None

    # Example method to validate all components
    def validate_all(self) -> dict[str, Any]:
        """Validate all components of the Vale configuration."""
        results = {}

        # Validate config
        try:
            results['config'] = self.config_manager.validate_config()
        except ConfigurationError as e:
            results['config'] = {'errors': [str(e)], 'warnings': []}

        # Validate packages
        packages = self.package_manager.list_packages()
        package_validations = {}
        for package in packages:
            package_validations[package] = self.package_manager.validate_package(package)
        results['packages'] = package_validations

        # Validate vocabularies
        vocabularies = self.vocabulary_manager.list_vocabularies()
        vocab_validations = {}
        for vocab in vocabularies:
            vocab_validations[vocab] = self.vocabulary_manager.validate_vocabulary(vocab)
        results['vocabularies'] = vocab_validations

        # Validate actions
        actions = self.action_manager.list_actions()
        action_validations = {}
        for action in actions:
            action_validations[action] = self.action_manager.validate_action(action)
        results['actions'] = action_validations

        # Validate styles
        styles = self.style_manager.list_styles()
        style_validations = {}
        for style in styles:
            style_validations[style] = self.style_manager.validate_style(style)
        results['styles'] = style_validations

        return results
