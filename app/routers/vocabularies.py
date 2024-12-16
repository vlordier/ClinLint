# app/routers/vocabularies.py

import csv
import logging
from io import StringIO
from pathlib import Path
from typing import Literal, Union

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi import Path as FastAPIPathParam
from starlette.responses import Response

from app.schemas.vale_schemas import ValeVocabulary
from app.schemas.vocabulary_schemas import VocabularyUpdate as UpdateVocabularyRequest
from app.services.config_loader import ConfigLoader, get_config_loader
from app.services.exceptions import ConfigurationError
from app.utils.helpers import load_terms

router = APIRouter()
logger = logging.getLogger(__name__)


def get_vocabularies_base_path(config_loader: ConfigLoader) -> Path:
    """Retrieve the base path for vocabularies from the configuration."""
    try:
        vale_config = config_loader.get_vale_config()
        vocab_base = Path(vale_config.get("styles_path", ".vale/styles")).resolve() / "config" / "vocabularies"
        if not vocab_base.exists():
            logger.warning(f"Vocabularies base path does not exist: {vocab_base}")
        return vocab_base
    except Exception as e:
        logger.error(f"Error retrieving vocabularies base path: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving vocabularies base path: {e}",
        ) from e


def load_vocabulary_file(vocab_file: Path) -> ValeVocabulary:
    """Load a single vocabulary file and return a ValeVocabulary object."""
    vocab_type = "accept" if "accept" in vocab_file.name else "reject"
    terms = load_terms(vocab_file)
    vocabulary = ValeVocabulary(
        name=vocab_file.stem,
        category=vocab_file.parent.name,
        terms=terms,
        type=vocab_type,
    )
    logger.debug(f"Loaded vocabulary '{vocab_file.stem}' with {len(terms)} terms.")
    return vocabulary


@router.get("/", summary="Get all available Vale vocabularies", response_model=dict[str, list[ValeVocabulary]])
async def get_vocabularies(
    config_loader: ConfigLoader = Depends()
) -> dict[str, list[ValeVocabulary]]:
    """Retrieve all available Vale vocabularies across all categories.

    Args:
        config_loader: Dependency-injected ConfigLoader instance.

    Returns:
        A dictionary with a list of ValeVocabulary objects.
    """
    logger.info("Retrieving all available vocabularies.")
    vocabularies = []
    try:
        vocab_base = get_vocabularies_base_path(config_loader)
        if not vocab_base.exists():
            logger.info(f"No vocabularies found at base path: {vocab_base}")
            return {"vocabularies": []}

        for category_dir in vocab_base.iterdir():
            if category_dir.is_dir():
                for vocab_file in category_dir.glob("**/*.txt"):
                    try:
                        vocabulary = load_vocabulary_file(vocab_file)
                        vocabularies.append(vocabulary)
                    except Exception as e:
                        logger.warning(f"Failed to load vocabulary file '{vocab_file}': {e}")
                        continue

        logger.info(f"Total vocabularies retrieved: {len(vocabularies)}")
        return {"vocabularies": vocabularies}

    except Exception as e:
        logger.error(f"Error retrieving vocabularies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving vocabularies: {e}",
        ) from e


@router.get(
    "/{category}",
    response_model=dict[str, list[ValeVocabulary]],
    summary="Get vocabularies for a specific category",
)
async def get_category_vocabularies(
    category: str = FastAPIPathParam(..., description="Name of the vocabulary category"),
    config_loader: ConfigLoader = Depends(),
) -> dict[str, list[ValeVocabulary]]:
    """Retrieve all vocabularies within a specific category.

    Args:
        category: The vocabulary category to retrieve.
        config_loader: Dependency-injected ConfigLoader instance.

    Returns:
        A dictionary with a list of ValeVocabulary objects within the specified category.

    Raises:
        HTTPException: If the category does not exist or an error occurs.
    """
    logger.info(f"Retrieving vocabularies for category: '{category}'")
    vocabularies = []
    try:
        vocab_base = get_vocabularies_base_path(config_loader)
        category_path = vocab_base / category

        if not category_path.exists() or not category_path.is_dir():
            logger.error(f"Category '{category}' not found at path: {category_path}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category '{category}' not found.",
            )

        vocab_files = list(category_path.glob("**/*.txt"))
        if not vocab_files:
            logger.warning(f"No vocabulary files found in category: '{category}'")
            return {"vocabularies": []}

        for vocab_file in vocab_files:
            try:
                vocabulary = load_vocabulary_file(vocab_file)
                vocabularies.append(vocabulary)
            except Exception as e:
                logger.warning(f"Failed to load vocabulary file '{vocab_file}': {e}")
                continue

        logger.info(f"Total vocabularies retrieved for category '{category}': {len(vocabularies)}")
        return {"vocabularies": vocabularies}

    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration error: {e}",
        ) from e
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving vocabularies for category '{category}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
        ) from e


@router.post(
    "/{category}/bulk",
    summary="Bulk update multiple vocabulary files in a category",
    response_model=dict[str, Union[str, dict[str, int]]],
)
async def bulk_update_vocabularies(
    category: str = FastAPIPathParam(..., description="Name of the vocabulary category"),
    updates: UpdateVocabularyRequest = Body(),
    config_loader: ConfigLoader = Depends(get_config_loader),
) -> dict[str, Union[str, dict[str, int]]]:
    """Bulk update multiple vocabulary files (accept/reject) within a specific category.

    Args:
        category: The vocabulary category to update.
        updates: The vocabulary terms to update, categorized by type.
        config_loader: Dependency-injected ConfigLoader instance.

    Returns:
        A dictionary indicating the success status and count of updated terms.

    Raises:
        HTTPException: If an error occurs during the update process.
    """
    logger.info(f"Bulk updating vocabularies for category: '{category}'")
    try:
        vocab_base = get_vocabularies_base_path(config_loader)
        category_path = vocab_base / category
        category_path.mkdir(parents=True, exist_ok=True)

        results = {}
        for vocab_type, terms in updates.terms.items():
            if vocab_type not in {"accept", "reject"}:
                logger.warning(f"Invalid vocabulary type '{vocab_type}' provided. Skipping.")
                continue

            vocab_file = category_path / f"{vocab_type}.txt"
            unique_terms = sorted(set(terms))
            try:
                with vocab_file.open("w", encoding="utf-8") as f:
                    f.write("\n".join(unique_terms))
                results[vocab_type] = len(unique_terms)
                logger.debug(f"Updated '{vocab_type}' vocabulary with {len(unique_terms)} terms.")
            except Exception as e:
                logger.error(f"Failed to update vocabulary file '{vocab_file}': {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to update vocabulary '{vocab_type}': {e}",
                ) from e

        logger.info(f"Successfully bulk updated vocabularies for category '{category}': {results}")
        return {
            "status": "success",
            "message": f"Updated vocabularies for category '{category}'.",
            "terms_count": results,
        }

    except Exception as e:
        logger.error(f"Error during bulk update of vocabularies for category '{category}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating vocabularies: {e}",
        ) from e


@router.put(
    "/{category}/{vocab_type}",
    summary="Update vocabulary terms for a category",
    response_model=dict[str, Union[str, int]],
)
async def update_vocabulary(
    category: str = FastAPIPathParam(..., description="Name of the vocabulary category"),
    vocab_type: Literal["accept", "reject"] = FastAPIPathParam(..., description="Type of vocabulary ('accept' or 'reject')"),
    request: UpdateVocabularyRequest = Body(),
    config_loader: ConfigLoader = Depends(get_config_loader),
) -> dict[str, Union[str, int]]:
    """Update vocabulary terms for a specific type within a category.

    Args:
        category: The vocabulary category to update.
        vocab_type: The type of vocabulary ('accept' or 'reject').
        request: The list of terms to update.
        config_loader: Dependency-injected ConfigLoader instance.

    Returns:
        A dictionary indicating the success status and count of updated terms.

    Raises:
        HTTPException: If an error occurs during the update process.
    """
    logger.info(f"Updating '{vocab_type}' vocabulary for category '{category}'.")
    try:
        vocab_base = get_vocabularies_base_path(config_loader)
        category_path = vocab_base / category
        category_path.mkdir(parents=True, exist_ok=True)

        vocab_file = category_path / f"{vocab_type}.txt"
        unique_terms = sorted(set(request.terms))

        try:
            with vocab_file.open("w", encoding="utf-8") as f:
                f.write("\n".join(unique_terms))
            logger.debug(f"Updated '{vocab_type}' vocabulary with {len(unique_terms)} terms.")
        except Exception as e:
            logger.error(f"Failed to update vocabulary file '{vocab_file}': {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update vocabulary '{vocab_type}': {e}",
            ) from e

        return {
            "status": "success",
            "message": f"Updated '{vocab_type}' vocabulary for category '{category}'.",
            "terms_count": len(unique_terms),
        }

    except Exception as e:
        logger.error(f"Error updating vocabulary '{vocab_type}' for category '{category}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating vocabulary: {e}",
        ) from e


@router.get(
    "/export/{category}",
    summary="Export vocabulary terms for a category",
)
async def export_vocabulary(
    category: str = FastAPIPathParam(..., description="Vocabulary category to export"),
    output_format: Literal["json", "csv"] = Query("json", description="Export format ('json' or 'csv')"),
    config_loader: ConfigLoader = Depends(get_config_loader),
) -> Union[dict[str, list[str]], Response]:
    """Export vocabulary terms for a specified category in JSON or CSV format.

    Args:
        category: The vocabulary category to export.
        output_format: The format to export the vocabulary terms ('json' or 'csv').
        config_loader: Dependency-injected ConfigLoader instance.

    Returns:
        A JSON dictionary or a CSV file containing the exported vocabulary terms.

    Raises:
        HTTPException: If the category does not exist or an error occurs during export.
    """
    logger.info(f"Exporting vocabularies for category '{category}' in '{output_format}' format.")
    try:
        vocab_base = get_vocabularies_base_path(config_loader)
        category_path = vocab_base / category

        if not category_path.exists() or not category_path.is_dir():
            logger.error(f"Category '{category}' not found at path: {category_path}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category '{category}' not found.",
            )

        terms: dict[str, list[str]] = {"accept": [], "reject": []}
        for vocab_file in category_path.glob("**/*.txt"):
            vocab_type = "accept" if "accept" in vocab_file.name else "reject"
            try:
                with vocab_file.open("r", encoding="utf-8") as f:
                    file_terms = [line.strip() for line in f if line.strip()]
                    terms[vocab_type].extend(file_terms)
                logger.debug(f"Loaded {len(file_terms)} terms from '{vocab_file.name}'.")
            except Exception as e:
                logger.warning(f"Failed to load terms from '{vocab_file}': {e}")
                continue

        if output_format.lower() == "csv":
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["Type", "Term"])
            for vocab_type, term_list in terms.items():
                for term in term_list:
                    writer.writerow([vocab_type, term])
            csv_content = output.getvalue()
            logger.info(f"Exported vocabularies for category '{category}' as CSV.")
            return Response(content=csv_content, media_type="text/csv")

        logger.info(f"Exported vocabularies for category '{category}' as JSON.")
        return terms

    except Exception as e:
        logger.error(f"Error exporting vocabularies for category '{category}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting vocabularies: {e}",
        ) from e
