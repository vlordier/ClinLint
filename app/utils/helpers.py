# app/utils/helpers.py

import logging
from pathlib import Path
from typing import Literal, Optional

import yaml
from fuzzywuzzy import fuzz

# from schemas.search_schemas import RuleSearchResult, ValeVocabulary
from schemas.search.rule_search_result import RuleSearchResult
from schemas.vale.vale_schemas import ValeVocabulary
from services.exceptions import ConfigurationError


def search_rules(
    styles_path: Path,
    query: str,
    min_similarity: float,
    severity: Optional[str],
    rule_type: Optional[str],
) -> list[RuleSearchResult]:
    """Search for rules in the given styles path."""
    rule_matches = []
    if styles_path.exists():
        for package_dir in styles_path.iterdir():
            if package_dir.is_dir():
                for rule_file in package_dir.glob("**/*.yml"):
                    try:
                        with open(rule_file) as f:
                            rule = yaml.safe_load(f) or {}

                            # Apply rule filters
                            if severity and rule.get("level") != severity:
                                continue
                            if rule_type and rule.get("extends") != rule_type:
                                continue

                            # Only process .yml files as rules
                            if rule_file.suffix == ".yml":
                                rule_text = str(rule).lower()
                                similarity = fuzz.partial_ratio(
                                    query.lower(), rule_text
                                )

                                if similarity >= min_similarity:
                                    rule_matches.append(
                                        RuleSearchResult(
                                            package=package_dir.name,
                                            rule=rule_file.stem,
                                            description=rule.get("description", ""),
                                            severity=rule.get("level", "suggestion"),
                                        )
                                    )
                    except yaml.YAMLError as e:
                        logging.error(f"YAML error in rule file {rule_file}: {e}")
                        continue
    return rule_matches


def load_terms(vocab_file: Path) -> list[str]:
    """Load terms from a vocabulary file."""
    with open(vocab_file) as f:
        return [line.strip() for line in f if line.strip()]


def filter_terms(terms: list[str], query: str, min_similarity: float) -> list[str]:
    """Filter terms based on fuzzy similarity."""
    return [
        term
        for term in terms
        if fuzz.partial_ratio(query.lower(), term.lower()) >= min_similarity
    ]


def create_vocabulary(
    vocab_file: Path, category_name: str, matching_terms: list[str], vocab_type: str
) -> ValeVocabulary:
    """Create a ValeVocabulary instance."""
    return ValeVocabulary(
        name=vocab_file.stem,
        category=category_name,
        terms=matching_terms,
        type=vocab_type,
    )


def search_vocabularies_helper(
    vocab_path: Path,
    query: str,
    min_similarity: float,
    categories: Optional[list[str]],
    vocab_type: Optional[Literal["accept", "reject"]],
) -> list[ValeVocabulary]:
    """Search for vocabularies in the given vocab path."""
    vocab_matches = []
    if not vocab_path.exists():
        return vocab_matches

    for category in vocab_path.iterdir():
        if not category.is_dir():
            continue
        if categories and category.name not in categories:
            continue

        for vocab_file in category.glob("**/*.txt"):
            current_type = "accept" if "accept" in vocab_file.name else "reject"
            if vocab_type and current_type != vocab_type:
                continue

            try:
                terms = load_terms(vocab_file)
                matching_terms = filter_terms(terms, query, min_similarity)
                if matching_terms:
                    vocabulary = create_vocabulary(
                        vocab_file, category.name, matching_terms, current_type
                    )
                    vocab_matches.append(vocabulary)
            except Exception as e:
                logging.error(f"Error processing vocabulary file {vocab_file}: {e}")
                logging.warning(f"Error processing vocabulary file {vocab_file}: {e}")
                continue

    return vocab_matches


def verify_config_file_exists(config_path: Path) -> None:
    """Verify that the configuration file exists."""
    if not config_path.exists():
        logging.error(f"Config file not found: {config_path}")
        raise ConfigurationError(
            f"Configuration file not found: {config_path}",
        )


def check_styles_path(vale_config: dict) -> Optional[Path]:
    """Check and return the styles path from the config."""
    styles_path = Path(vale_config.get("styles_path", ""))
    if not styles_path:
        return None
    return styles_path


def validate_package_structure(styles_path: Path) -> list[str]:
    """Validate the package structure and collect warnings."""
    warnings = []
    packages_checked = 0
    for package_dir in styles_path.iterdir():
        if package_dir.is_dir():
            packages_checked += 1
            rule_files = list(package_dir.glob("*.yml"))
            if not rule_files:
                warnings.append(f"No rule files found in package: {package_dir.name}")
            logging.debug(
                f"Checked package {package_dir.name}: found {len(rule_files)} rule files"
            )
    if packages_checked == 0:
        warnings.append("No packages found in styles directory")
    return warnings


def validate_vocabulary_structure(vale_config: dict) -> list[str]:
    """Validate the vocabulary structure and collect warnings."""
    warnings = []
    vocab_path = Path(vale_config.get("styles_path", "")) / "config" / "vocabularies"
    if vocab_path.exists():
        categories_checked = 0
        for category in vocab_path.iterdir():
            if category.is_dir():
                categories_checked += 1
                accept_file = category / "accept.txt"
                reject_file = category / "reject.txt"
                if not accept_file.exists() and not reject_file.exists():
                    warnings.append(
                        f"No vocabulary files found in category: {category.name}"
                    )
                logging.debug(
                    f"Checked category {category.name}: accept={accept_file.exists()}, reject={reject_file.exists()}"
                )
        if categories_checked == 0:
            warnings.append("No vocabulary categories found")
    return warnings


def count_rules(styles_path: Path) -> tuple[dict[str, int], int]:
    """Count the number of rules per package and total rules.

    Args:
        styles_path: Path to Vale styles directory

    Returns:
        Tuple containing:
        - Dict mapping package names to rule counts
        - Total number of rules across all packages
    """
    packages = {}
    total_rules = 0

    if not styles_path.exists():
        return packages, total_rules

    for package_dir in styles_path.iterdir():
        if package_dir.is_dir():
            try:
                # Count .yml files recursively
                rule_files = list(package_dir.glob("**/*.yml"))
                valid_rules = []

                # Validate each rule file
                for rule_file in rule_files:
                    try:
                        with open(rule_file) as f:
                            if yaml.safe_load(f):  # Check if valid YAML
                                valid_rules.append(rule_file)
                    except Exception as e:
                        logging.warning(f"Invalid rule file {rule_file}: {e}")
                        continue

                rule_count = len(valid_rules)
                if rule_count > 0:
                    packages[package_dir.name] = rule_count
                    total_rules += rule_count

            except Exception as e:
                logging.warning(f"Error counting rules in {package_dir}: {e}")
                continue

    return packages, total_rules


def count_vocabularies(vocab_path: Path) -> dict[str, int]:
    """Count the number of vocabularies per category.

    Args:
        vocab_path: Path to vocabularies directory

    Returns:
        Dict mapping category names to vocabulary counts
    """
    vocab_counts = {}
    if not vocab_path.exists():
        return vocab_counts

    for category in vocab_path.iterdir():
        if category.is_dir():
            try:
                # Count .txt files recursively
                vocab_files = list(category.glob("**/*.txt"))
                valid_vocabs = []

                # Validate each vocabulary file
                for vocab_file in vocab_files:
                    try:
                        with open(vocab_file) as f:
                            if any(line.strip() for line in f):  # Check if has content
                                valid_vocabs.append(vocab_file)
                    except Exception as e:
                        logging.warning(f"Invalid vocabulary file {vocab_file}: {e}")
                        continue

                vocab_count = len(valid_vocabs)
                if vocab_count > 0:
                    vocab_counts[category.name] = vocab_count

            except Exception as e:
                logging.warning(f"Error counting vocabularies in {category}: {e}")
                continue

    return vocab_counts
