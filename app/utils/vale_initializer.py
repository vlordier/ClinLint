import logging
from pathlib import Path

from services.config_loader import ConfigLoader
from services.rule_validator import RuleValidator
from services.vocabulary_validator import VocabularyValidator
from utils.helpers import (
    validate_package_structure,
    validate_vocabulary_structure,
    verify_config_file_exists,
)

logger = logging.getLogger(__name__)

def validate_vale_directory(vale_directory: Path):
    """Validate all rules, styles, packages, and vocabularies in the .vale directory."""
    logger.info(f"Validating Vale directory: {vale_directory}")

    # Validate packages
    package_warnings = validate_package_structure(vale_directory / "styles")
    if package_warnings:
        logger.warning(f"Package structure warnings: {package_warnings}")

    # Validate vocabularies
    vocab_warnings = validate_vocabulary_structure({"styles_path": str(vale_directory)})
    if vocab_warnings:
        logger.warning(f"Vocabulary structure warnings: {vocab_warnings}")

    # Validate individual rules and vocabularies
    rule_validator = RuleValidator()
    vocab_validator = VocabularyValidator()

    # Validate rules
    rule_files = list((vale_directory / "styles").glob("**/*.yml"))
    for rule_file in rule_files:
        try:
            rule_validator.validate_rule_file(rule_file)
            logger.info(f"Validated rule file: {rule_file}")
        except Exception as e:
            logger.error(f"Error validating rule file {rule_file}: {e}")
            logger.error(f"Error validating rule file {rule_file}: {e}")

    # Validate vocabularies
    vocab_files = list((vale_directory / "config/vocabularies").glob("**/*.txt"))
    for vocab_file in vocab_files:
        try:
            vocab_validator.validate_vocabulary_file(vocab_file)
            logger.info(f"Validated vocabulary file: {vocab_file}")
        except Exception as e:
            logger.error(f"Error validating vocabulary file {vocab_file}: {e}")

    logger.info("Validation of Vale directory completed.")
    """Initialize and validate all vocabularies, rules, configs, and packages."""
    try:
        # Load configuration (will initialize default if needed)
        config_loader = ConfigLoader()
        vale_config = config_loader.get_vale_config()
        logger.debug(f"Configuration loaded from: {config_loader.config_path}")
        logger.debug(f"Vale config contents: {vale_config}")

        # Verify config file exists
        config_path = Path(config_loader.config_path)
        verify_config_file_exists(config_path)
        logger.debug(f"Config file verified at: {config_path}")

        # Validate package structure
        styles_path = Path(vale_config.get("styles_path", ".vale/styles")).resolve()
        logger.debug(f"Checking styles path: {styles_path}")
        package_warnings = validate_package_structure(styles_path)
        if package_warnings:
            logger.warning(f"Package structure warnings: {package_warnings}")

        # Validate vocabulary structure
        vocab_warnings = validate_vocabulary_structure(vale_config)
        if vocab_warnings:
            logger.warning(f"Vocabulary structure warnings: {vocab_warnings}")

        # Validate vocabularies
        vocab_validator = VocabularyValidator()
        vocab_path = styles_path / "config" / "vocabularies"
        logger.debug(f"Checking vocabulary path: {vocab_path}")
        vocab_files = list(vocab_path.glob("**/*.txt"))
        logger.debug(f"Found vocabulary files: {vocab_files}")
        vocab_updates = [vocab_validator.validate_vocabulary_file(f) for f in vocab_files]
        logger.info(f"Validated vocabularies: {vocab_updates}")

        # Validate rules
        rule_validator = RuleValidator()
        rule_files = list(styles_path.glob("**/*.yml"))
        logger.debug(f"Found rule files: {rule_files}")
        rule_definitions = [rule_validator.validate_rule_file(f) for f in rule_files]
        logger.info(f"Validated rules: {rule_definitions}")

        logger.info("Initialization and validation completed successfully.")

    except Exception as e:
        logger.error(f"Error during initialization and validation: {e}")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    validate_vale_directory(Path(".vale"))
