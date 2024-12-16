#!/usr/bin/env python3
"""Validate Vale configuration and package structure."""

import sys
from pathlib import Path

import yaml


def validate_package_structure(styles_path: Path) -> list[str]:
    """Validate the Vale styles package structure."""
    errors = []

    # Check core config exists
    if not (styles_path / "CSR" / "config.yml").exists():
        errors.append("Missing core config.yml")

    # Required directories
    required_dirs = [
        "core",
        "packages",
        "rules",
        "Document_Structure_and_Sections",
        "Safety_Reporting",
        "Efficacy_Reporting",
        "Statistical_Considerations",
        "Regulatory_Compliance",
    ]

    for dir_name in required_dirs:
        if not (styles_path / "CSR" / dir_name).exists():
            errors.append(f"Missing required directory: {dir_name}")

    return errors


def validate_yaml_file(file_path: Path) -> list[str]:
    """Validate YAML file syntax."""
    errors = []
    try:
        with open(file_path) as f:
            yaml.safe_load(f)
    except yaml.YAMLError as e:
        errors.append(f"YAML syntax error in {file_path}: {str(e)}")
    return errors


def validate_rule_files(styles_path: Path) -> list[str]:
    """Validate individual rule files."""
    errors = []

    for rule_file in styles_path.rglob("*.yml"):
        # Skip directories
        if rule_file.is_dir():
            continue

        # Validate YAML syntax
        errors.extend(validate_yaml_file(rule_file))

        # Validate rule structure
        try:
            with open(rule_file) as f:
                rule = yaml.safe_load(f)

            # Check required fields
            if not isinstance(rule, dict):
                errors.append(f"{rule_file}: Rule must be a dictionary")
                continue

            if "extends" not in rule:
                errors.append(f"{rule_file}: Missing 'extends' field")

            if "message" not in rule:
                errors.append(f"{rule_file}: Missing 'message' field")

            if "level" not in rule:
                errors.append(f"{rule_file}: Missing 'level' field")

            # Validate level value
            valid_levels = ["suggestion", "warning", "error"]
            if rule.get("level") not in valid_levels:
                errors.append(
                    f"{rule_file}: Invalid level '{rule.get('level')}'. Must be one of {valid_levels}"
                )

        except Exception as e:
            errors.append(f"Error validating {rule_file}: {str(e)}")

    return errors


def main():
    """Main validation function."""
    styles_path = Path(".vale/styles")

    if not styles_path.exists():
        print("Error: .vale/styles directory not found")
        sys.exit(1)

    errors = []

    # Validate package structure
    errors.extend(validate_package_structure(styles_path))

    # Validate rule files
    errors.extend(validate_rule_files(styles_path))

    # Report results
    if errors:
        print("\nValidation errors found:")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)
    else:
        print("\nValidation successful! No errors found.")
        sys.exit(0)


if __name__ == "__main__":
    main()
