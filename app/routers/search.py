# app/routers/search.py

import logging
import re
from pathlib import Path
from typing import Literal, Optional

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Query,
    status,
)

from app.schemas.csr_schemas import CSR
from app.schemas.search_schemas import CSRSearchParams, SearchResults
from app.schemas.vale_schemas import ValeVocabulary
from app.services.config_loader import ConfigLoader, get_config_loader
from app.utils.helpers import search_rules, search_vocabularies_helper

router = APIRouter()
logger = logging.getLogger(__name__)


def get_vale_paths(config_loader: ConfigLoader) -> dict[str, Path]:
    """Retrieve essential Vale paths from the configuration.

    Args:
        config_loader: Dependency-injected ConfigLoader instance.

    Returns:
        A dictionary containing styles and vocabularies paths.

    Raises:
        HTTPException: If paths cannot be retrieved.
    """
    try:
        vale_config = config_loader.get_vale_config()
        styles_path = Path(vale_config.get("styles_path", ".vale/styles")).resolve()
        vocab_path = styles_path / "config" / "vocabularies"
        return {"styles_path": styles_path, "vocab_path": vocab_path}
    except Exception as e:
        logger.error(f"Error retrieving Vale paths: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving Vale paths: {e}",
        ) from e


@router.get("/csr", summary="Search for CSRs", response_model=list[CSR])
async def search_csr(
    params: CSRSearchParams = Body(),
    min_similarity: float = Query(
        default=70.0,
        ge=0.0,
        le=100.0,
        description="Minimum similarity score for fuzzy matching (0-100)",
    ),
) -> list[CSR]:
    """Search for CSRs based on various parameters.

    Args:
        params: Parameters for CSR search.
        min_similarity: Minimum similarity score for fuzzy matching.

    Returns:
        A list of CSRs matching the search criteria.

    Raises:
        HTTPException: If an error occurs during the search process.
    """
    logger.info(f"Initiating CSR search with parameters: {params} and min_similarity: {min_similarity}")
    try:
        # Implement the actual search logic here.
        # Placeholder for demonstration purposes.
        results = search_rules(
            styles_path=Path(".vale/styles"),  # Replace with actual path if necessary
            query=params.query,
            min_similarity=min_similarity,
            severity=params.severity,
            rule_type=params.rule_type,
        )
        logger.debug(f"CSR search completed with {len(results)} results.")
        return results
    except Exception as e:
        logger.error(f"Error occurred during CSR search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during CSR search: {e}",
        ) from e


@router.get(
    "/",
    response_model=SearchResults,
    summary="Search across all Vale rules and vocabularies",
)
async def search_all(
    query: str = Query(..., min_length=1, description="Search term"),
    min_similarity: float = Query(
        default=70.0,
        ge=0.0,
        le=100.0,
        description="Minimum similarity score (0-100) for fuzzy matching",
    ),
    categories: Optional[list[str]] = Query(),
    severity: Optional[str] = Query(None, description="Filter rules by severity"),
    rule_type: Optional[str] = Query(None, description="Filter rules by type"),
    vocab_type: Optional[Literal["accept", "reject"]] = Query(
        None, description="Filter vocabularies by type"
    ),
    config_loader: ConfigLoader = Depends(),
) -> SearchResults:
    """Search across all Vale rules and vocabularies with fuzzy matching.

    Args:
        query: Search term.
        min_similarity: Minimum similarity score for fuzzy matching.
        categories: Filter vocabularies by categories.
        severity: Filter rules by severity.
        rule_type: Filter rules by type.
        vocab_type: Filter vocabularies by type.
        config_loader: Dependency-injected ConfigLoader instance.

    Returns:
        Combined search results for rules and vocabularies.

    Raises:
        HTTPException: If an error occurs during the search process.
    """
    logger.info(f"Initiating comprehensive search with query: '{query}' and min_similarity: {min_similarity}")
    try:
        paths = get_vale_paths(config_loader)
        styles_path = paths["styles_path"]
        vocab_path = paths["vocab_path"]

        rule_matches = search_rules(
            styles_path=styles_path,
            query=query,
            min_similarity=min_similarity,
            severity=severity,
            rule_type=rule_type,
        )
        vocab_matches = search_vocabularies_helper(
            vocab_path=vocab_path,
            query=query,
            min_similarity=min_similarity,
            categories=categories,
            vocab_type=vocab_type,
        )

        total_rule_matches = len(rule_matches)
        total_vocab_matches = sum(len(v.terms) for v in vocab_matches)

        logger.debug(f"Found {total_rule_matches} rule matches and {total_vocab_matches} vocabulary matches.")

        return SearchResults(
            rules=rule_matches,
            vocabularies=vocab_matches,
            total_matches=total_rule_matches + total_vocab_matches,
            rule_matches=total_rule_matches,
            vocabulary_matches=total_vocab_matches,
        )
    except Exception as e:
        logger.error(f"Error occurred during comprehensive search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during comprehensive search: {e}",
        ) from e


@router.get(
    "/vocabularies",
    summary="Search across Vale vocabularies",
    response_model=dict[str, list[ValeVocabulary]],
)
async def search_vocabularies_endpoint(
    query: str = Query(..., min_length=1, description="Search term"),
    categories: Optional[list[str]] = Query(None, description="Filter vocabularies by categories"),
    vocab_type: Optional[Literal["accept", "reject"]] = Query(
        None, description="Filter vocabularies by type"
    ),
    config_loader: ConfigLoader = Depends(get_config_loader),
) -> dict[str, list[ValeVocabulary]]:
    """Search across Vale vocabularies.

    Args:
        query: Search term.
        categories: Filter vocabularies by categories.
        vocab_type: Filter vocabularies by type.
        config_loader: Dependency-injected ConfigLoader instance.

    Returns:
        A dictionary containing the search results.

    Raises:
        HTTPException: If an error occurs during the search process.
    """
    logger.info(f"Initiating vocabulary search with query: '{query}', categories: {categories}, vocab_type: {vocab_type}")
    try:
        paths = get_vale_paths(config_loader)
        vocab_path = paths["vocab_path"]

        if not vocab_path.exists():
            logger.warning(f"Vocabularies path does not exist: {vocab_path}")
            return {"results": []}

        results = []
        for category_dir in vocab_path.iterdir():
            if category_dir.is_dir() and (not categories or category_dir.name in categories):
                for vocab_file in category_dir.glob("**/*.txt"):
                    current_type = "accept" if "accept" in vocab_file.name else "reject"
                    if vocab_type and current_type != vocab_type:
                        continue

                    try:
                        with vocab_file.open("r", encoding="utf-8") as f:
                            terms = [line.strip() for line in f if line.strip()]
                        matching_terms = [
                            term for term in terms if re.search(query, term, re.IGNORECASE)
                        ]
                        if matching_terms:
                            vocabulary = ValeVocabulary(
                                name=vocab_file.stem,
                                category=category_dir.name,
                                terms=matching_terms,
                                type=current_type,
                            )
                            results.append(vocabulary)
                            logger.debug(f"Found {len(matching_terms)} matching terms in '{vocab_file.name}'.")
                    except Exception as e:
                        logger.warning(f"Failed to process vocabulary file '{vocab_file}': {e}")
                        continue

        logger.info(f"Vocabulary search completed with {len(results)} results.")
        return {"results": results}

    except Exception as e:
        logger.error(f"Error occurred during vocabulary search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during vocabulary search: {e}",
        ) from e
