# app/routers/rules.py

import logging
import re
from pathlib import Path

import yaml
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi import Path as FastAPIPath

from app.schemas.vale_schemas import (
    PackageStats,
    RuleContent,
    RuleHistory,
    RuleMetadata,
    RuleValidationRequest,
    UpdateRuleTagsRequest,
    ValidationResult,
)
from app.services.config_loader import ConfigLoader, get_config_loader

router = APIRouter()
logger = logging.getLogger(__name__)


def load_rule_file(config_loader: ConfigLoader, package_name: str, rule_name: str) -> dict:
    """Helper function to load a rule file."""
    rule_path = Path(config_loader.get_vale_config()["styles_path"]).resolve() / package_name / f"{rule_name}.yml"
    if not rule_path.exists():
        logger.error(f"Rule not found: {rule_name}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule not found: {rule_name}",
        )
    try:
        with rule_path.open() as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        logger.error(f"YAML error while loading rule {rule_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing rule file: {e}",
        ) from e


@router.get("/", summary="Get available Vale rules", response_model=dict)
def get_vale_rules(config_loader: ConfigLoader = Depends()) -> dict:
    config_loader = get_config_loader()
    """Retrieve all available Vale rules."""
    rules = config_loader.get_vale_config().get("rules", [])
    logger.debug(f"Retrieved {len(rules)} rules.")
    return {"rules": rules}


@router.post(
    "/validate",
    response_model=ValidationResult,
    summary="Validate a Vale rule definition",
)
async def validate_rule(
    request: RuleValidationRequest,
) -> ValidationResult:
    """Validate the structure and content of a Vale rule definition."""
    logger.info(f"Validating rule: {request.rule_name}")

    errors = []
    warnings = []

    # Required fields validation
    required_fields = {"message", "level", "scope"}
    missing_fields = required_fields - request.rule_content.keys()
    if missing_fields:
        errors.extend([f"Missing required field: {field}" for field in missing_fields])

    # Severity level validation
    valid_levels = {"suggestion", "warning", "error"}
    level = request.rule_content.get("level")
    if level and level not in valid_levels:
        errors.append(f"Invalid severity level: '{level}'. Must be one of {valid_levels}.")

    # Pattern validity
    pattern = request.rule_content.get("pattern")
    if pattern:
        try:
            re.compile(pattern)
        except re.error as e:
            errors.append(f"Invalid regex pattern: {e}")

    is_valid = not errors
    if is_valid:
        logger.info(f"Rule '{request.rule_name}' is valid.")
    else:
        logger.warning(f"Rule '{request.rule_name}' validation failed with errors: {errors}")

    return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)


@router.get(
    "/{package_name}/{rule_name}/metadata",
    response_model=RuleMetadata,
    summary="Get metadata for a specific rule",
)
async def get_rule_metadata(
    package_name: str = FastAPIPath(..., description="Name of the package"),
    rule_name: str = FastAPIPath(..., description="Name of the rule"),
    config_loader: ConfigLoader = Depends(),
) -> RuleMetadata:
    """Fetch metadata for a specified Vale rule."""
    rule_data = load_rule_file(config_loader, package_name, rule_name)

    metadata = RuleMetadata(
        name=rule_name,
        version=rule_data.get("version", "1.0.0"),
        last_updated=rule_data.get("last_updated", ""),
        author=rule_data.get("author"),
        tags=set(rule_data.get("tags", [])),
    )
    logger.debug(f"Metadata for rule '{rule_name}': {metadata}")
    return metadata


@router.get(
    "/{package_name}/{rule_name}/history",
    response_model=list[RuleHistory],
    summary="Get version history for a specific rule",
)
async def get_rule_history(
    package_name: str = FastAPIPath(..., description="Name of the package"),
    rule_name: str = FastAPIPath(..., description="Name of the rule"),
    config_loader: ConfigLoader = Depends(get_config_loader),
) -> list[RuleHistory]:
    """Retrieve the version history of a specified Vale rule."""
    rule_data = load_rule_file(config_loader, package_name, rule_name)
    history_entries = rule_data.get("history", [])

    history = []
    for entry in history_entries:
        try:
            history.append(RuleHistory(**entry))
        except TypeError as e:
            logger.warning(f"Invalid history entry in rule '{rule_name}': {entry} - {e}")
            continue

    logger.debug(f"Retrieved {len(history)} history entries for rule '{rule_name}'.")
    return history


@router.post(
    "/{package_name}/{rule_name}/tags",
    summary="Update tags for a specific rule",
    response_model=dict,
)
async def update_rule_tags(
    package_name: str = FastAPIPath(..., description="Name of the package"),
    rule_name: str = FastAPIPath(..., description="Name of the rule"),
    request: UpdateRuleTagsRequest = Body(),
    config_loader: ConfigLoader = Depends(get_config_loader),
) -> dict:
    """Update the tags associated with a specific Vale rule."""
    rule_path = Path(config_loader.get_vale_config()["styles_path"]) / package_name / f"{rule_name}.yml"

    try:
        rule_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing rule data or initialize an empty dictionary
        if rule_path.exists():
            with rule_path.open() as f:
                rule_data = yaml.safe_load(f) or {}
        else:
            rule_data = {}
            logger.info(f"Creating new rule file at {rule_path}")

        # Update tags if provided
        if request.tags is not None:
            rule_data["tags"] = list(request.tags)
            logger.debug(f"Updating tags for rule '{rule_name}': {request.tags}")

        # Write back to the YAML file
        with rule_path.open("w") as f:
            yaml.safe_dump(rule_data, f)

        return {
            "status": "success",
            "message": f"Updated tags for rule '{rule_name}'.",
            "tags": rule_data.get("tags", []),
        }

    except yaml.YAMLError as e:
        logger.error(f"YAML error while updating tags for rule '{rule_name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating tags: {e}",
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error while updating tags for rule '{rule_name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update tags: {e}",
        ) from e


@router.put(
    "/{package_name}/{rule_name}",
    summary="Update an existing Vale rule",
    response_model=dict,
)
async def update_rule(
    package_name: str = FastAPIPath(..., description="Name of the package"),
    rule_name: str = FastAPIPath(..., description="Name of the rule"),
    rule_content: RuleContent = Body(),
    config_loader: ConfigLoader = Depends(get_config_loader),
) -> dict:
    """Update the content of an existing Vale rule after validation."""
    rule_path = Path(config_loader.get_vale_config()["styles_path"]) / package_name / f"{rule_name}.yml"

    try:
        # Ensure the directory exists
        rule_path.parent.mkdir(parents=True, exist_ok=True)

        # Validate the new rule content
        validation_request = RuleValidationRequest(
            rule_name=rule_name, rule_content=rule_content.dict()
        )
        validation = await validate_rule(validation_request)

        if not validation.is_valid:
            logger.warning(f"Validation failed for rule '{rule_name}': {validation.errors}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid rule content: {', '.join(validation.errors)}",
            )

        # Write the validated rule content to the file
        with rule_path.open("w") as f:
            yaml.safe_dump(rule_content.dict(), f)

        logger.info(f"Rule '{rule_name}' updated successfully.")
        return {
            "status": "success",
            "message": f"Rule '{rule_name}' updated successfully.",
        }

    except HTTPException:
        raise
    except yaml.YAMLError as e:
        logger.error(f"YAML error while updating rule '{rule_name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating rule: {e}",
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error while updating rule '{rule_name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update rule: {e}",
        ) from e


@router.get(
    "/{package_name}/stats",
    response_model=PackageStats,
    summary="Get detailed statistics for a package",
)
async def get_package_statistics(
    package_name: str = FastAPIPath(..., description="Name of the package"),
    config_loader: ConfigLoader = Depends(get_config_loader),
) -> PackageStats:
    """Compute and return statistics for a specified Vale package."""
    vale_config = config_loader.get_vale_config()
    package_path = Path(vale_config.get("styles_path", ".vale/styles")) / package_name

    if not package_path.exists():
        logger.error(f"Package not found: {package_name}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Package not found: {package_name}",
        )

    total_rules = 0
    rules_by_severity = {"suggestion": 0, "warning": 0, "error": 0}
    rules_by_category = {}
    active_rules = 0

    try:
        for rule_file in package_path.rglob("*.yml"):
            with rule_file.open() as f:
                try:
                    rule = yaml.safe_load(f) or {}
                    total_rules += 1

                    # Count by severity
                    severity = rule.get("level", "suggestion")
                    rules_by_severity[severity] = rules_by_severity.get(severity, 0) + 1

                    # Count by category
                    category = rule.get("category", "uncategorized")
                    rules_by_category[category] = rules_by_category.get(category, 0) + 1

                    # Count active rules
                    if rule.get("active", True):
                        active_rules += 1

                except yaml.YAMLError as e:
                    logger.warning(f"YAML error in file '{rule_file}': {e}")
                    continue

        stats = PackageStats(
            total_rules=total_rules,
            rules_by_severity=rules_by_severity,
            rules_by_category=rules_by_category,
            active_rules=active_rules,
        )
        logger.debug(f"Statistics for package '{package_name}': {stats}")
        return stats

    except Exception as e:
        logger.error(f"Error computing statistics for package '{package_name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compute package statistics: {e}",
        ) from e
