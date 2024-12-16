import logging
from pathlib import Path

from typing import Any, Optional

from app.services.vale_config_manager import ValeConfigManager

def main():
    """
    Main function to manage Vale configuration and validate resources.
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize ValeConfigManager
    manager = ValeConfigManager()

    # Define paths (if needed elsewhere)
    vale_ini_path = manager.path_manager.vale_ini
    styles_path = manager.path_manager.styles_path
    packages_path = manager.path_manager.packages_path
    actions_path = manager.path_manager.actions_path

    # Ensure .vale.ini exists and configure StylesPath
    if not vale_ini_path.exists():
        manager.config_manager.create_config()
        logging.info(f"Created default config at: {vale_ini_path}")

    config = manager.config_manager.load_config()
    env_styles_path = str(styles_path.resolve())

    if not config.has_option("DEFAULT", "StylesPath") or config["DEFAULT"]["StylesPath"] != env_styles_path:
        manager.config_manager.update_config("DEFAULT", {"StylesPath": env_styles_path})
        logging.info(f"Updated config with StylesPath at: {env_styles_path}")

    # Load and validate configuration
    try:
        config = manager.config_manager.load_config()
        validation_results = manager.config_manager.validate_config()
        logging.info(f"Config loaded: {config.sections()}")
        logging.info(f"Config validation results: {validation_results}")
    except Exception as e:
        logging.error(f"Error loading or validating config: {e}")

    # Ensure styles, packages, and actions directories exist
    # (Already handled by PathManager during initialization)

    # Validate all components
    try:
        overall_validation = manager.validate_all()
        logging.info(f"Overall validation results: {overall_validation}")
    except Exception as e:
        logging.error(f"Error during overall validation: {e}")

    # Load and validate packages
    packages = manager.package_manager.list_packages()
    logging.info(f"Available packages: {packages} (Total: {len(packages)})")
    for package in packages:
        is_valid = manager.package_manager.validate_package(package)
        logging.info(f"Package '{package}' is valid: {is_valid}")

    # Load and validate vocabularies
    vocabularies = manager.vocabulary_manager.list_vocabularies()
    logging.info(f"Available vocabularies: {vocabularies} (Total: {len(vocabularies)})")
    for vocab in vocabularies:
        is_valid = manager.vocabulary_manager.validate_vocabulary(vocab)
        logging.info(f"Vocabulary '{vocab}' is valid: {is_valid}")

    # Load and validate actions
    actions = manager.action_manager.list_actions()
    logging.info(f"Available actions: {actions} (Total: {len(actions)})")
    for action in actions:
        is_valid = manager.action_manager.validate_action(action)
        logging.info(f"Action '{action}' is valid: {is_valid}")

    # Load and validate styles
    styles = manager.style_manager.list_styles()
    logging.info(f"Available styles: {styles} (Total: {len(styles)})")
    for style in styles:
        is_valid = manager.style_manager.validate_style(style)
        logging.info(f"Style '{style}' is valid: {is_valid}")

if __name__ == "__main__":
    main()
