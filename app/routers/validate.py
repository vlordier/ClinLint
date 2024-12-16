# app/routers/validate.py

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from app.schemas.vale_schemas import RuleValidationRequest, ValidationResult
from app.schemas.vocabulary_schemas import VocabularyUpdate
from app.services.config_loader import ConfigLoader, get_config_loader
from app.services.exceptions import ConfigurationError
from app.services.llm_feedback import LLMFeedback
from app.services.rule_validator import RuleValidator
from app.services.vale_runner import run_vale_on_text
from app.services.vocabulary_validator import VocabularyValidator
from app.utils.helpers import (
    check_styles_path,
    validate_package_structure,
    validate_vocabulary_structure,
    verify_config_file_exists,
)

router = APIRouter()


@router.post(
    "/config",
    response_model=ValidationResult,
    summary="Validate a Vale configuration file",
)
async def validate_vale_config(
    config_path: str = Query(..., description="Path to Vale config file"),
    config_loader: ConfigLoader = None,
) -> ValidationResult:
    """Validate a Vale configuration file.

    Args:
        config_path: Path to the Vale configuration file to validate.
        config_loader: Configuration loader dependency.

    config_loader: Configuration loader dependency.

    Returns:
        ValidationResult containing validation status and any errors/warnings.

    Raises:
        HTTPException: If config file invalid or inaccessible.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Validating Vale config at: {config_path}")

    get_config_loader()
    config_path_obj = Path(config_path)
    verify_config_file_exists(config_path_obj)

    # Reload config_loader with the new config path
    new_config_loader = ConfigLoader(config_path)
    vale_config = new_config_loader.get_vale_config()

    errors = []
    warnings = []

    # Check required paths
    styles_path = check_styles_path(vale_config)
    if not styles_path:
        errors.append("styles_path not specified in config")
    elif not styles_path.exists():
        errors.append(f"Styles path does not exist: {styles_path}")

    # Check package structure
    if styles_path and styles_path.exists():
        package_warnings = validate_package_structure(styles_path)
        warnings.extend(package_warnings)

    # Check vocabulary structure
    vocab_warnings = validate_vocabulary_structure(vale_config)
    warnings.extend(vocab_warnings)

    validation_result = ValidationResult(
        is_valid=len(errors) == 0, errors=errors, warnings=warnings
    )

    try:
        logger.info(
            f"Validation complete: valid={validation_result.is_valid}, errors={len(errors)}, warnings={len(warnings)}"
        )
        return validation_result

    except ConfigurationError as e:
        logger.error(f"Configuration error during validation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Configuration error: {str(e)}",
        ) from e
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in validate_vale_config: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        ) from e


@router.post(
    "/rules/batch", response_model=list[dict], summary="Validate multiple Vale rules"
)
async def validate_rules_batch(
    rules: list[RuleValidationRequest],
    config_loader: ConfigLoader,
    use_llm: bool = Query(False, description="Use LLM for validation assistance"),
    max_attempts: int = Query(3, description="Maximum LLM fix attempts per rule")
) -> list[dict]:
    """Validate multiple Vale rules in batch.

    Args:
        rules: List of rules to validate
        use_llm: Whether to use LLM for validation assistance
        max_attempts: Maximum number of LLM fix attempts per rule
        config_loader: Configuration loader dependency

    Returns:
        List of validation results for each rule
    """
    validator = RuleValidator(
        llm_feedback=LLMFeedback("v1", config_loader) if use_llm else None
    )
    return validator.validate_rules_batch(
        [rule.rule_content for rule in rules], use_llm, max_attempts
    )


@router.post(
    "/vocabularies/batch",
    response_model=list[dict],
    summary="Validate multiple Vale vocabularies",
)
async def validate_vocabularies_batch(
    vocabularies: list[VocabularyUpdate],
    config_loader: ConfigLoader,
) -> list[dict]:
    """Validate multiple Vale vocabularies in batch.

    Args:
        vocabularies: List of vocabularies to validate
        config_loader: Configuration loader dependency

    Returns:
        List of validation results for each vocabulary
    """
    validator = VocabularyValidator()
    return validator.validate_vocabularies_batch(vocabularies)


@router.post(
    "/rule", response_model=dict, summary="Validate text against specified Vale rules"
)
async def validate_text_with_rule(
    request: RuleValidationRequest,
    config_loader: ConfigLoader,
) -> dict:
    """Validate text against specified Vale rules and vocabularies.

    Args:
        request: Rule validation request containing rules, vocabularies, and text
        config_loader: Configuration loader dependency

    Returns:
        dict containing validation results and any error messages
    """
    try:
        vale_config = config_loader.get_vale_config()

        # Create temporary rule config with specified rules and vocabularies
        rule_config = {}
        for rule in request.rules:
            rule_config[rule] = "YES"

        vocab_config = {}
        for vocab in request.vocabularies:
            vocab_config[vocab] = "YES"

        temporary_config = {
            "StylesPath": vale_config.get("styles_path", ".vale/styles"),
            "MinAlertLevel": "suggestion",
            "Vocabularies": vocab_config,
            "[*]": rule_config,
        }

        # Here you might need to write the temporary config to a temporary file
        # and pass its path to run_vale_on_text. For simplicity, assuming run_vale_on_text can accept the config dict.

        # Run Vale validation
        results = run_vale_on_text(request.text, temporary_config)

        # If LLM judge requested, get additional feedback
        llm_feedback = None
        if request.use_llm:
            llm_judge = LLMFeedback("v1", config_loader)
            llm_feedback = llm_judge.get_feedback(
                request.text, "improvement_prompt", vale_issues=results
            )

        return {
            "rules": request.rules,
            "vocabularies": request.vocabularies,
            "vale_issues": results,
            "llm_feedback": llm_feedback,
            "text": request.text,
            "summary": {
                "total_rules": len(request.rules),
                "total_vocabularies": len(request.vocabularies),
                "total_issues": sum(len(issues) for issues in results.values()),
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
