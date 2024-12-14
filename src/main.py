"""FastAPI application for text analysis and suggestion generation."""

import logging
import re
from pathlib import Path
from typing import Literal, Optional, Union

import yaml
from fastapi import Body, FastAPI, HTTPException, Path as PathParam, Query, status
from pydantic import BaseModel, Field

from services.config_loader import ConfigLoader
from services.exceptions import ConfigurationError
from services.llm_judge import LLMJudge
from services.suggestion_chain import AnalysisMode, ChainConfig, SuggestionChain

from .services.config import Config

app = FastAPI(
    title="ClinLint API",
    description="API for clinical document analysis and suggestions",
    version="1.0.0",
)

config = Config()  # Initialize global config


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., json_schema_extra={"example": "healthy"})
    version: str = Field(..., json_schema_extra={"example": "1.0.0"})


class SuggestionInput(BaseModel):
    """Input model for single text analysis request."""

    text: str = Field(..., description="Text to analyze")
    vale_config: str = Field(..., description="Vale configuration path")
    llm_template: str = Field(..., description="LLM template name")
    section_name: Optional[str] = Field(None, description="Document section name")


class BatchInput(BaseModel):
    """Input model for batch text analysis request."""

    texts: list[SuggestionInput] = Field(..., description="List of texts to analyze")


class CustomAnalysisInput(BaseModel):
    """Input model for custom analysis configuration."""

    text: str = Field(..., description="Text to analyze")
    mode: AnalysisMode = Field(..., description="Analysis mode")
    vale_rules: Optional[list[str]] = Field(None, description="Vale rules to apply")
    llm_templates: Optional[list[str]] = Field(None, description="LLM templates to use")


class ValePackage(BaseModel):
    """Model for Vale package information."""

    name: str = Field(..., description="Package name")
    description: Optional[str] = Field(None, description="Package description")
    rules: list[str] = Field(
        default_factory=list, description="Available rules in package"
    )


class ValeVocabulary(BaseModel):
    """Model for Vale vocabulary information."""

    name: str = Field(..., description="Vocabulary name")
    category: str = Field(..., description="Vocabulary category")
    terms: list[str] = Field(default_factory=list, description="Terms in vocabulary")
    type: str = Field(..., description="Vocabulary type (accept/reject)")


class ValeStats(BaseModel):
    """Model for Vale statistics."""

    total_packages: int = Field(..., description="Total number of packages")
    total_rules: int = Field(..., description="Total number of rules")
    total_vocabularies: int = Field(..., description="Total number of vocabularies")
    rules_per_package: dict[str, int] = Field(
        ..., description="Number of rules per package"
    )
    vocab_per_category: dict[str, int] = Field(
        ..., description="Number of vocabularies per category"
    )


class ValidationResult(BaseModel):
    """Model for Vale configuration validation results."""

    is_valid: bool = Field(..., description="Whether the configuration is valid")
    errors: list[str] = Field(
        default_factory=list, description="List of validation errors"
    )
    warnings: list[str] = Field(
        default_factory=list, description="List of validation warnings"
    )


class RuleValidationRequest(BaseModel):
    """Model for rule validation request."""

    rule_name: str = Field(..., description="Name of the rule to validate")
    rule_content: dict = Field(..., description="Rule definition to validate")


class RuleSearchResult(BaseModel):
    """Model for rule search results."""

    package: str = Field(..., description="Package containing the rule")
    rule: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    severity: str = Field(..., description="Rule severity")


class RuleMetadata(BaseModel):
    """Model for rule metadata."""

    name: str = Field(..., description="Rule name")
    version: str = Field(..., description="Rule version")
    last_updated: str = Field(..., description="Last update timestamp")
    author: Optional[str] = Field(None, description="Rule author")
    tags: set[str] = Field(default_factory=set, description="Rule tags")


class RuleHistory(BaseModel):
    """Model for rule version history."""

    version: str = Field(..., description="Version number")
    changes: list[str] = Field(..., description="List of changes")
    timestamp: str = Field(..., description="Change timestamp")
    author: Optional[str] = Field(None, description="Change author")


class PackageStats(BaseModel):
    """Model for package statistics."""

    total_rules: int = Field(..., description="Total number of rules")
    rules_by_severity: dict[str, int] = Field(
        ..., description="Rules count by severity"
    )
    rules_by_category: dict[str, int] = Field(
        ..., description="Rules count by category"
    )
    active_rules: int = Field(..., description="Number of active rules")


@app.get("/health")
def health_check() -> HealthResponse:
    """Check API health status."""
    return HealthResponse(status="healthy", version="1.0.0")


@app.get("/rules")
def get_vale_rules() -> dict:
    """Get available Vale rules."""
    try:
        config_loader = ConfigLoader(config.config_path)
        return {"rules": config_loader.get_vale_config().get("rules", [])}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@app.get("/packages")
def get_vale_packages() -> dict:
    """Get available Vale packages."""
    try:
        config_loader = ConfigLoader(config.config_path)
        packages = []
        vale_config = config_loader.get_vale_config()

        # Get packages from Vale styles directory
        styles_path = Path(vale_config.get("styles_path", ".vale/styles"))
        if styles_path.exists():
            for package_dir in styles_path.iterdir():
                if package_dir.is_dir():
                    package = ValePackage(
                        name=package_dir.name,
                        rules=[rule.stem for rule in package_dir.glob("**/*.yml")],
                    )
                    packages.append(package)

        return {"packages": [p.dict() for p in packages]}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@app.get("/vocabularies")
async def get_vocabularies() -> dict[str, list[ValeVocabulary]]:
    """Get all available Vale vocabularies."""
    try:
        config_loader = ConfigLoader(config.config_path)
        vale_config = config_loader.get_vale_config()

        # Get vocabularies from Vale config directory
        vocab_path = Path(
            vale_config.get("styles_path", ".vale/styles/config/vocabularies")
        )
        if not vocab_path.exists():
            return {"vocabularies": []}

        vocabularies = []
        for category in vocab_path.iterdir():
            if category.is_dir():
                for vocab_file in category.glob("**/*.txt"):
                    vocab_type = "accept" if "accept" in vocab_file.name else "reject"
                    with open(vocab_file) as f:
                        terms = [line.strip() for line in f if line.strip()]

                    vocabularies.append(
                        ValeVocabulary(
                            name=vocab_file.stem,
                            category=category.name,
                            terms=terms,
                            type=vocab_type,
                        )
                    )

        return {"vocabularies": vocabularies}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@app.get("/vocabularies/{category}", response_model=dict[str, list[ValeVocabulary]])
async def get_category_vocabularies(
    category: str = PathParam(..., description="Category name"),
) -> dict[str, list[ValeVocabulary]]:
    """Get vocabularies for a specific category.

    Args:
        category: The vocabulary category to retrieve

    Returns:
        Dict containing list of ValeVocabulary objects

    Raises:
        HTTPException: If category not found or error accessing files
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Getting vocabularies for category: {category}")

    try:
        config_loader = ConfigLoader(config.config_path)
        vale_config = config_loader.get_vale_config()

        # Validate category path
        vocab_base = Path(
            vale_config.get("styles_path", ".vale/styles/config/vocabularies")
        )
        if not vocab_base.exists():
            logger.error(f"Vocabularies base path does not exist: {vocab_base}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vocabularies directory not found",
            )

        category_path = vocab_base / category
        if not category_path.exists():
            logger.error(f"Category path does not exist: {category_path}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category '{category}' not found",
            )

        vocabularies = []
        vocab_files = list(category_path.glob("**/*.txt"))

        if not vocab_files:
            logger.warning(f"No vocabulary files found in category: {category}")
            return {"vocabularies": []}

        for vocab_file in vocab_files:
            try:
                vocab_type = "accept" if "accept" in vocab_file.name else "reject"
                with open(vocab_file) as f:
                    terms = [line.strip() for line in f if line.strip()]

                vocabulary = ValeVocabulary(
                    name=vocab_file.stem,
                    category=category,
                    terms=terms,
                    type=vocab_type,
                )
                vocabularies.append(vocabulary)
                logger.debug(
                    f"Loaded vocabulary {vocab_file.stem} with {len(terms)} terms"
                )

            except Exception as e:
                logger.warning(f"Error loading vocabulary file {vocab_file}: {e}")
                continue

        logger.info(
            f"Successfully retrieved {len(vocabularies)} vocabularies for category {category}"
        )
        return {"vocabularies": vocabularies}

    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration error: {str(e)}",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_category_vocabularies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@app.post("/rules/validate", response_model=ValidationResult)
async def validate_rule(request: RuleValidationRequest) -> ValidationResult:
    """Validate a Vale rule definition."""
    logger = logging.getLogger(__name__)
    logger.info(f"Validating rule: {request.rule_name}")

    try:
        errors = []
        warnings = []

        # Check required fields
        required_fields = ["message", "level", "scope"]
        for field in required_fields:
            if field not in request.rule_content:
                errors.append(f"Missing required field: {field}")

        # Validate severity level
        valid_levels = ["suggestion", "warning", "error"]
        if "level" in request.rule_content:
            level = request.rule_content["level"]
            if level not in valid_levels:
                errors.append(
                    f"Invalid severity level: {level}. Must be one of {valid_levels}"
                )

        # Check pattern validity
        if "pattern" in request.rule_content:
            try:
                re.compile(request.rule_content["pattern"])
            except re.error as e:
                errors.append(f"Invalid regex pattern: {e}")

        return ValidationResult(
            is_valid=len(errors) == 0, errors=errors, warnings=warnings
        )

    except Exception as e:
        logger.error(f"Error validating rule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rule validation failed: {str(e)}",
        )


@app.get("/vocabularies/export/{category}")
async def export_vocabulary(
    category: str = PathParam(..., description="Vocabulary category to export"),
    output_format: str = Query("json", description="Export format (json/csv)"),
) -> Union[dict, str]:
    """Export vocabulary terms for a category."""
    try:
        config_loader = ConfigLoader(config.config_path)
        vale_config = config_loader.get_vale_config()
        vocab_path = Path(
            vale_config.get("styles_path", ".vale/styles/config/vocabularies")
        )

        category_path = vocab_path / category
        if not category_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category not found: {category}",
            )

        terms = {"accept": [], "reject": []}
        for vocab_file in category_path.glob("**/*.txt"):
            vocab_type = "accept" if "accept" in vocab_file.name else "reject"
            with open(vocab_file) as f:
                terms[vocab_type].extend(line.strip() for line in f if line.strip())

        if output_format.lower() == "csv":
            import csv
            from io import StringIO

            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["Type", "Term"])
            for term_type, term_list in terms.items():
                for term in term_list:
                    writer.writerow([term_type, term])
            return output.getvalue()

        return terms

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/rules/{package_name}/{rule_name}/metadata", response_model=RuleMetadata)
async def get_rule_metadata(
    package_name: str = PathParam(..., description="Package name"),
    rule_name: str = PathParam(..., description="Rule name"),
) -> RuleMetadata:
    """Get metadata for a specific rule."""
    try:
        rule_path = (
            Path(config.config.vale.styles_path)
            / package_name
            / f"{rule_name}.yml"
        )

        if not rule_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rule not found: {rule_name}",
            )

        with open(rule_path) as f:
            rule_data = yaml.safe_load(f)

        return RuleMetadata(
            name=rule_name,
            version=rule_data.get("version", "1.0.0"),
            last_updated=rule_data.get("last_updated", ""),
            author=rule_data.get("author"),
            tags=set(rule_data.get("tags", [])),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/rules/{package_name}/{rule_name}/history", response_model=list[RuleHistory])
async def get_rule_history(
    package_name: str = PathParam(..., description="Package name"),
    rule_name: str = PathParam(..., description="Rule name"),
) -> list[RuleHistory]:
    """Get version history for a specific rule."""
    try:
        rule_path = (
            Path(config.config.vale.styles_path)
            / package_name
            / f"{rule_name}.yml"
        )

        if not rule_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rule not found: {rule_name}",
            )

        with open(rule_path) as f:
            rule_data = yaml.safe_load(f)

        history = rule_data.get("history", [])
        return [RuleHistory(**entry) for entry in history]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post("/rules/{package_name}/{rule_name}/tags")
async def update_rule_tags(
    package_name: str = PathParam(description="Package name"),
    rule_name: str = PathParam(description="Rule name"),
    tags: set[str] = None,
) -> dict:
    """Update tags for a specific rule."""
    try:
        config_loader = ConfigLoader(config.config_path)
        vale_config = config_loader.get_vale_config()
        rule_path = (
            Path(config.config.vale.styles_path)
            / package_name
            / f"{rule_name}.yml"
        )

        # Create parent directories if they don't exist
        rule_path.parent.mkdir(parents=True, exist_ok=True)

        # Create the rule file if it doesn't exist
        if not rule_path.exists():
            with open(rule_path, "w") as f:
                yaml.safe_dump({}, f)

        with open(rule_path) as f:
            rule_data = yaml.safe_load(f)

        rule_data["tags"] = list(tags)

        with open(rule_path, "w") as f:
            yaml.safe_dump(rule_data, f)

        return {
            "status": "success",
            "message": f"Updated tags for rule {rule_name}",
            "tags": list(tags),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post("/vocabularies/{category}/bulk")
async def bulk_update_vocabularies(
    category: str, updates: dict[Literal["accept", "reject"], list[str]]
) -> dict:
    """Bulk update multiple vocabulary files in a category."""
    try:
        config_loader = ConfigLoader(config.config_path)
        vale_config = config_loader.get_vale_config()
        vocab_path = Path(
            vale_config.get("styles_path", ".vale/styles/config/vocabularies")
        )

        category_path = vocab_path / category
        if not category_path.exists():
            category_path.mkdir(parents=True)

        results = {}
        for vocab_type, terms in updates.items():
            vocab_file = category_path / f"{vocab_type}.txt"
            with open(vocab_file, "w") as f:
                f.write("\n".join(sorted(set(terms))))
            results[vocab_type] = len(terms)

        return {
            "status": "success",
            "message": f"Updated vocabularies for {category}",
            "terms_count": results,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/packages/{package_name}/stats", response_model=PackageStats)
async def get_package_statistics(
    package_name: str = PathParam(..., description="Package name"),
) -> PackageStats:
    """Get detailed statistics for a package."""
    try:
        config_loader = ConfigLoader(config.config_path)
        vale_config = config_loader.get_vale_config()
        package_path = (
            Path(vale_config.get("styles_path", ".vale/styles")) / package_name
        )

        if not package_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Package not found: {package_name}",
            )

        total_rules = 0
        rules_by_severity = {"suggestion": 0, "warning": 0, "error": 0}
        rules_by_category = {}
        active_rules = 0

        for rule_file in package_path.glob("**/*.yml"):
            with open(rule_file) as f:
                try:
                    rule = yaml.safe_load(f)
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

                except yaml.YAMLError:
                    continue

        return PackageStats(
            total_rules=total_rules,
            rules_by_severity=rules_by_severity,
            rules_by_category=rules_by_category,
            active_rules=active_rules,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.put("/rules/{package_name}/{rule_name}")
async def update_rule(
    package_name: str = PathParam(..., description="Package name"),
    rule_name: str = PathParam(..., description="Rule name"),
    rule_content: dict = Body(..., description="Updated rule content"),
) -> dict:
    """Update an existing Vale rule."""
    try:
        rule_path = (
            Path(config.config.vale.styles_path)
            / package_name
            / f"{rule_name}.yml"
        )

        # Create parent directories if they don't exist
        rule_path.parent.mkdir(parents=True, exist_ok=True)

        # Validate rule content
        validation = await validate_rule(
            RuleValidationRequest(rule_name=rule_name, rule_content=rule_content)
        )

        if not validation.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid rule content: {', '.join(validation.errors)}",
            )

        # Write updated rule
        with open(rule_path, "w") as f:
            yaml.safe_dump(rule_content, f)
        return {
            "status": "success",
            "message": f"Rule {rule_name} updated successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update rule: {str(e)}",
        )


@app.put("/vocabularies/{category}/{vocab_type}")
async def update_vocabulary(
    terms: list[str],
    category: str = PathParam(..., description="Category name"),
    vocab_type: Literal["accept", "reject"] = PathParam(..., description="Vocabulary type"),
) -> dict:
    """Update vocabulary terms for a category.

    Args:
        category: Vocabulary category
        vocab_type: Type of vocabulary (accept/reject)
        terms: List of terms to update

    Returns:
        Dict containing update status
    """
    try:
        config_loader = ConfigLoader(config.config_path)
        vale_config = config_loader.get_vale_config()
        vocab_path = Path(
            vale_config.get("styles_path", ".vale/styles/config/vocabularies")
        )

        category_path = vocab_path / category
        if not category_path.exists():
            category_path.mkdir(parents=True)

        vocab_file = category_path / f"{vocab_type}.txt"

        # Write updated terms
        with open(vocab_file, "w") as f:
            f.write("\n".join(sorted(set(terms))))

        return {
            "status": "success",
            "message": f"Updated {vocab_type} vocabulary for {category}",
            "terms_count": len(terms),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/search/rules", response_model=list[RuleSearchResult])
async def search_rules(
    query: str = Query(..., min_length=1, description="Search term"),
    severity: Optional[str] = Query(default=None, description="Filter by severity"),
    category: Optional[str] = Query(default=None, description="Filter by category"),
) -> list[RuleSearchResult]:
    """Search for rules across all packages."""
    try:
        config_loader = ConfigLoader(config.config_path)
        vale_config = config_loader.get_vale_config()
        styles_path = Path(vale_config.get("styles_path", ".vale/styles"))

        results = []
        for package_dir in styles_path.iterdir():
            if package_dir.is_dir():
                for rule_file in package_dir.glob("**/*.yml"):
                    with open(rule_file) as f:
                        try:
                            rule = yaml.safe_load(f)

                            # Apply filters
                            if severity and rule.get("level") != severity:
                                continue
                            if category and rule.get("category") != category:
                                continue

                            # Search in rule content
                            rule_text = str(rule).lower()
                            if query.lower() in rule_text:
                                results.append(
                                    RuleSearchResult(
                                        package=package_dir.name,
                                        rule=rule_file.stem,
                                        description=rule.get("description", ""),
                                        severity=rule.get("level", "suggestion"),
                                    )
                                )

                        except yaml.YAMLError:
                            continue

        return results

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/statistics", response_model=ValeStats)
async def get_vale_statistics() -> ValeStats:
    """Get statistics about Vale packages, rules, and vocabularies.

    Returns:
        ValeStats: Statistics about packages, rules and vocabularies

    Raises:
        HTTPException: If there's an error accessing files or processing data
    """
    logger = logging.getLogger(__name__)
    logger.info("Getting Vale statistics")

    try:
        config_loader = ConfigLoader(config.config_path)
        vale_config = config_loader.get_vale_config()
        styles_path = Path(vale_config.get("styles_path", ".vale/styles"))
        vocab_path = Path(
            vale_config.get("styles_path", ".vale/styles/config/vocabularies")
        )

        if not styles_path.exists():
            logger.error(f"Styles path does not exist: {styles_path}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Styles directory not found: {styles_path}",
            )

        # Count packages and rules
        packages = {}
        total_rules = 0
        for package_dir in styles_path.iterdir():
            if package_dir.is_dir():
                try:
                    rule_count = len(list(package_dir.glob("**/*.yml")))
                    packages[package_dir.name] = rule_count
                    total_rules += rule_count
                    logger.debug(
                        f"Counted {rule_count} rules in package {package_dir.name}"
                    )
                except Exception as e:
                    logger.warning(f"Error counting rules in {package_dir}: {e}")
                    continue

        # Count vocabularies per category
        vocab_counts = {}
        if vocab_path.exists():
            for category in vocab_path.iterdir():
                if category.is_dir():
                    try:
                        vocab_count = len(list(category.glob("**/*.txt")))
                        vocab_counts[category.name] = vocab_count
                        logger.debug(
                            f"Counted {vocab_count} vocabularies in {category.name}"
                        )
                    except Exception as e:
                        logger.warning(
                            f"Error counting vocabularies in {category}: {e}"
                        )
                        continue

        stats = ValeStats(
            total_packages=len(packages),
            total_rules=total_rules,
            total_vocabularies=sum(vocab_counts.values()),
            rules_per_package=packages,
            vocab_per_category=vocab_counts,
        )
        logger.info(
            f"Successfully gathered Vale statistics: {len(packages)} packages, {total_rules} rules"
        )
        return stats

    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_vale_statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@app.get("/search/vocabularies")
async def search_vocabularies(
    query: str = Query(..., min_length=1, description="Search term"),
    categories: Optional[list[str]] = Query(
        default=None, description="Filter by categories"
    ),
    vocab_type: Optional[Literal["accept", "reject"]] = Query(
        default=None, description="Filter by vocabulary type"
    ),
) -> dict[str, list[ValeVocabulary]]:
    """Search across Vale vocabularies."""
    try:
        config_loader = ConfigLoader(config.config_path)
        vale_config = config_loader.get_vale_config()
        vocab_path = Path(
            vale_config.get("styles_path", ".vale/styles/config/vocabularies")
        )

        if not vocab_path.exists():
            return {"results": []}

        results = []
        for category in vocab_path.iterdir():
            if category.is_dir() and (not categories or category.name in categories):
                for vocab_file in category.glob("**/*.txt"):
                    current_type = "accept" if "accept" in vocab_file.name else "reject"
                    if vocab_type and current_type != vocab_type:
                        continue

                    with open(vocab_file) as f:
                        terms = [line.strip() for line in f if line.strip()]
                        # Search in terms
                        matching_terms = [
                            term
                            for term in terms
                            if re.search(query, term, re.IGNORECASE)
                        ]
                        if matching_terms:
                            results.append(
                                ValeVocabulary(
                                    name=vocab_file.stem,
                                    category=category.name,
                                    terms=matching_terms,
                                    type=current_type,
                                )
                            )

        return {"results": results}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post("/validate/config", response_model=ValidationResult)
async def validate_vale_config(
    config_path: str = Query(..., description="Path to Vale config file"),
) -> ValidationResult:
    """Validate a Vale configuration file.

    Args:
        config_path: Path to the Vale configuration file to validate

    Returns:
        ValidationResult containing validation status and any errors/warnings

    Raises:
        HTTPException: If config file invalid or inaccessible
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Validating Vale config at: {config_path}")

    try:
        # Verify config file exists
        if not Path(config_path).exists():
            logger.error(f"Config file not found: {config_path}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Configuration file not found: {config_path}",
            )

        config_loader = ConfigLoader(config_path)
        vale_config = config_loader.get_vale_config()

        errors = []
        warnings = []

        # Check required paths
        styles_path = Path(vale_config.get("styles_path", ""))
        if not styles_path:
            errors.append("styles_path not specified in config")
        elif not styles_path.exists():
            errors.append(f"Styles path does not exist: {styles_path}")

        # Check package structure
        if styles_path.exists():
            packages_checked = 0
            for package_dir in styles_path.iterdir():
                if package_dir.is_dir():
                    packages_checked += 1
                    # Check for required files
                    rule_files = list(package_dir.glob("*.yml"))
                    if not rule_files:
                        warnings.append(
                            f"No rule files found in package: {package_dir.name}"
                        )
                    logger.debug(
                        f"Checked package {package_dir.name}: found {len(rule_files)} rule files"
                    )

            if packages_checked == 0:
                warnings.append("No packages found in styles directory")

        # Check vocabulary structure
        vocab_path = (
            Path(vale_config.get("styles_path", "")) / "config" / "vocabularies"
        )
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
                    logger.debug(
                        f"Checked category {category.name}: accept={accept_file.exists()}, reject={reject_file.exists()}"
                    )

            if categories_checked == 0:
                warnings.append("No vocabulary categories found")

        validation_result = ValidationResult(
            is_valid=len(errors) == 0, errors=errors, warnings=warnings
        )

        logger.info(
            f"Validation complete: valid={validation_result.is_valid}, errors={len(errors)}, warnings={len(warnings)}"
        )
        return validation_result

    except ConfigurationError as e:
        logger.error(f"Configuration error during validation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error in validate_vale_config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@app.get("/packages/{package_name}/rules")
def get_package_rules(package_name: str) -> dict:
    """Get rules for a specific Vale package."""
    try:
        config_loader = ConfigLoader(config.config_path)
        vale_config = config_loader.get_vale_config()

        # Check package directory
        package_path = (
            Path(vale_config.get("styles_path", ".vale/styles")) / package_name
        )
        if not package_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Package {package_name} not found",
            )

        # Get all rules in package
        rules = []
        for rule_file in package_path.glob("**/*.yml"):
            with open(rule_file) as f:
                try:
                    rule_content = yaml.safe_load(f)
                    rules.append(
                        {
                            "name": rule_file.stem,
                            "description": rule_content.get("description", ""),
                            "path": str(rule_file.relative_to(package_path)),
                        }
                    )
                except yaml.YAMLError:
                    continue

        return {"package": package_name, "rules": rules}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/templates")
def get_llm_templates() -> dict:
    """Get available LLM templates."""
    try:
        config_loader = ConfigLoader(config.config_path)
        return {"templates": config_loader.get_llm_config().get("templates", [])}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post("/suggestions")
def get_suggestions(suggestion_input: SuggestionInput) -> dict:
    """Generate suggestions for improving a single text."""
    try:
        config_loader = ConfigLoader(config.config_path)
        llm_judge = LLMJudge("v1", config_loader)
        suggestion_chain = SuggestionChain(suggestion_input.vale_config, llm_judge)

        chain_config = ChainConfig(
            mode=AnalysisMode.COMBINED,
            vale_rules=["CSR.Precision", "CSR.Consistency"],
            llm_templates=[suggestion_input.llm_template],
            section_name=suggestion_input.section_name,
        )

        return suggestion_chain.generate_suggestions(
            suggestion_input.text, config=chain_config
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post("/suggestions/batch")
def get_batch_suggestions(batch_input: BatchInput) -> dict:
    """Generate suggestions for improving multiple texts in batch."""
    try:
        config_loader = ConfigLoader(config.config_path)
        llm_judge = LLMJudge("v1", config_loader)
        suggestion_chain = SuggestionChain(batch_input.texts[0].vale_config, llm_judge)
        results = []

        for text_input in batch_input.texts:
            chain_config = ChainConfig(
                mode=AnalysisMode.COMBINED,
                vale_rules=["CSR.Precision", "CSR.Consistency"],
                llm_templates=[text_input.llm_template],
                section_name=text_input.section_name,
            )
            result = suggestion_chain.generate_suggestions(
                text_input.text, config=chain_config
            )
            results.append(result)
        return {"results": results}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post("/analyze/custom")
def analyze_with_custom_config(analysis_input: CustomAnalysisInput) -> dict:
    """Analyze text with custom configuration."""
    try:
        config_loader = ConfigLoader(config.config_path)
        llm_judge = LLMJudge("v1", config_loader)
        suggestion_chain = SuggestionChain(config.config.vale.config_path, llm_judge)

        chain_config = ChainConfig(
            mode=analysis_input.mode,
            vale_rules=analysis_input.vale_rules,
            llm_templates=analysis_input.llm_templates,
        )

        return suggestion_chain.generate_suggestions(
            analysis_input.text, config=chain_config
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
