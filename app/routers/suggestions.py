# app/routers/suggestions.py

import logging

from fastapi import APIRouter, Body, Depends, HTTPException, status
from pydantic import BaseModel

from app.schemas.search_schemas import BatchInput, CustomAnalysisInput, SuggestionInput
from app.services.config_loader import ConfigLoader, get_config_loader
from app.services.llm_feedback import LLMFeedback
from app.services.suggestion_chain import AnalysisMode, ChainConfig, SuggestionChain

router = APIRouter()
logger = logging.getLogger(__name__)


# Define response models (assuming they are not already defined)
class SuggestionResult(BaseModel):
    suggestions: list[str]
    metadata: dict[str, str]  # Example metadata


class BatchSuggestionResult(BaseModel):
    results: list[SuggestionResult]


class CustomAnalysisResult(BaseModel):
    analysis: dict[str, str]  # Example structure


def create_chain_config(
    mode: AnalysisMode,
    vale_rules: list[str],
    llm_templates: list[str],
    section_name: str = "",
) -> ChainConfig:
    """Helper function to create a ChainConfig object.

    Args:
        mode: The analysis mode.
        vale_rules: List of Vale rules to apply.
        llm_templates: List of LLM templates to use.
        section_name: Optional section name for the analysis.

    Returns:
        An instance of ChainConfig.
    """
    return ChainConfig(
        mode=mode,
        vale_rules=vale_rules,
        llm_templates=llm_templates,
        section_name=section_name,
    )


def initialize_suggestion_chain(vale_config: dict, llm_feedback_version: str = "v1") -> SuggestionChain:
    """Helper function to initialize a SuggestionChain with LLMFeedback.

    Args:
        vale_config: Configuration for Vale.
        llm_feedback_version: Version of LLMFeedback to use.

    Returns:
        An instance of SuggestionChain.
    """
    llm_feedback = LLMFeedback(llm_feedback_version, vale_config)
    return SuggestionChain(vale_config, llm_feedback)


@router.post(
    "/",
    summary="Generate suggestions for a single text",
    response_model=SuggestionResult,
    status_code=status.HTTP_200_OK,
)
def get_suggestions(
    suggestion_input: SuggestionInput = Body(),
    config_loader: ConfigLoader = Depends(),
) -> SuggestionResult:
    """Generate suggestions for improving a single text.

    Args:
        suggestion_input: Input data containing the text and configuration for suggestions.
        config_loader: Dependency-injected ConfigLoader instance.

    Returns:
        A SuggestionResult containing the generated suggestions and metadata.

    Raises:
        HTTPException: If an error occurs during the suggestion generation process.
    """
    logger.info(f"Generating suggestions for text: {suggestion_input.text[:30]}...")

    try:
        vale_config = config_loader.get_vale_config()
        suggestion_chain = initialize_suggestion_chain(vale_config)

        chain_config = create_chain_config(
            mode=AnalysisMode.COMBINED,
            vale_rules=["CSR.Precision", "CSR.Consistency"],
            llm_templates=[suggestion_input.llm_template],
            section_name=suggestion_input.section_name,
        )

        suggestions = suggestion_chain.generate_suggestions(
            suggestion_input.text, config=chain_config
        )

        logger.debug(f"Generated {len(suggestions)} suggestions for the input text.")

        return SuggestionResult(
            suggestions=suggestions,
            metadata={"source": "suggestion_chain_v1"},
        )

    except Exception as e:
        logger.error(f"Error generating suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating suggestions: {e}",
        ) from e


@router.post(
    "/batch",
    summary="Generate suggestions for multiple texts in batch",
    response_model=BatchSuggestionResult,
    status_code=status.HTTP_200_OK,
)
def get_batch_suggestions(
    batch_input: BatchInput = Body(),
    config_loader: ConfigLoader = Depends(get_config_loader),
) -> BatchSuggestionResult:
    """Generate suggestions for improving multiple texts in batch.

    Args:
        batch_input: Input data containing multiple texts and configurations for suggestions.
        config_loader: Dependency-injected ConfigLoader instance.

    Returns:
        A BatchSuggestionResult containing the generated suggestions for each input text.

    Raises:
        HTTPException: If no texts are provided or an error occurs during processing.
    """
    logger.info("Starting batch suggestion generation.")

    if not batch_input.texts:
        logger.warning("No texts provided for batch processing.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No texts provided for batch processing.",
        )

    try:
        vale_config = config_loader.get_vale_config()
        suggestion_chain = initialize_suggestion_chain(vale_config)

        results = []
        for idx, text_input in enumerate(batch_input.texts, start=1):
            logger.debug(f"Processing text {idx}/{len(batch_input.texts)}.")

            chain_config = create_chain_config(
                mode=AnalysisMode.COMBINED,
                vale_rules=["CSR.Precision", "CSR.Consistency"],
                llm_templates=[text_input.llm_template],
                section_name=text_input.section_name,
            )

            suggestions = suggestion_chain.generate_suggestions(
                text_input.text, config=chain_config
            )

            results.append(
                SuggestionResult(
                    suggestions=suggestions,
                    metadata={"source": "suggestion_chain_v1", "index": idx},
                )
            )

        logger.info(f"Batch suggestion generation completed with {len(results)} results.")

        return BatchSuggestionResult(results=results)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during batch suggestion generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during batch suggestion generation: {e}",
        ) from e


@router.post(
    "/custom",
    summary="Analyze text with custom configuration",
    response_model=SuggestionResult,
    status_code=status.HTTP_200_OK,
)
def analyze_with_custom_config(
    analysis_input: CustomAnalysisInput = Body(),
    config_loader: ConfigLoader = Depends(get_config_loader),
) -> SuggestionResult:
    """Analyze text with custom configuration.

    Args:
        analysis_input: Input data containing the text and custom configuration for analysis.
        config_loader: Dependency-injected ConfigLoader instance.

    Returns:
        A SuggestionResult containing the analysis suggestions and metadata.

    Raises:
        HTTPException: If an error occurs during the analysis process.
    """
    logger.info(f"Analyzing text with custom configuration: {analysis_input.text[:30]}...")

    try:
        vale_config = config_loader.get_vale_config()
        suggestion_chain = initialize_suggestion_chain(vale_config)

        chain_config = ChainConfig(
            mode=analysis_input.mode,
            vale_rules=analysis_input.vale_rules,
            llm_templates=analysis_input.llm_templates,
            section_name=analysis_input.section_name or "",
        )

        suggestions = suggestion_chain.generate_suggestions(
            analysis_input.text, config=chain_config
        )

        logger.debug(f"Generated {len(suggestions)} suggestions for custom analysis.")

        return SuggestionResult(
            suggestions=suggestions,
            metadata={"source": "suggestion_chain_custom"},
        )

    except Exception as e:
        logger.error(f"Error during custom analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during custom analysis: {e}",
        ) from e
