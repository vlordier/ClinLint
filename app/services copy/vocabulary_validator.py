"""Service for validating Vale vocabularies."""

import logging
from typing import Any

from schemas.vale.vocabulary_schemas import VocabularyCategory, VocabularyUpdate

logger = logging.getLogger(__name__)


class VocabularyValidator:
    """Handles Vale vocabulary validation."""

    def create_and_save_vocabulary(self, vocab_data: dict, save_path: str) -> dict[str, Any]:
        """Create a new vocabulary, validate it, and save if valid.

        Args:
            vocab_data: Dictionary containing vocabulary definition
            save_path: Path to save the valid vocabulary

        Returns:
            dict containing validation results and save status
        """
        logger.info(f"Creating vocabulary: {vocab_data}")

        validation_result = self.validate_vocabulary(VocabularyUpdate(**vocab_data))

        if validation_result["is_valid"]:
            try:
                # Save the vocabulary to the specified path
                with open(save_path, 'w') as file:
                    file.write(VocabularyUpdate(**vocab_data).json(indent=4))
                validation_result["save_status"] = "Vocabulary saved successfully"
            except Exception as e:
                logger.error(f"Error saving vocabulary: {e}")
                logger.error(f"Error saving vocabulary: {str(e)}")
                validation_result["save_status"] = "Vocabulary not saved due to save error"
        else:
            validation_result["save_status"] = "Vocabulary not saved due to validation errors"

        return validation_result
    def validate_vocabularies_batch(
        self, vocabularies: list[VocabularyUpdate]
    ) -> list[dict[str, Any]]:
        """Validate multiple vocabularies in batch.

        Args:
            vocabularies: List of vocabulary updates to validate

        Returns:
            List of validation results for each vocabulary
        """
        return [self.validate_vocabulary(vocab) for vocab in vocabularies]

    def validate_vocabulary(self, vocabulary: VocabularyUpdate) -> dict[str, Any]:
        """Validate a single vocabulary update.

        Args:
            vocabulary: Vocabulary update to validate

        Returns:
            dict containing validation results
        """
        logger.info(f"Validating vocabulary: {vocabulary.dict()}")

        validation_result = {"is_valid": True, "errors": [], "warnings": []}

        # Validate terms
        if not vocabulary.terms:
            validation_result["is_valid"] = False
            validation_result["errors"].append("Terms list cannot be empty")

        # Validate category
        try:
            VocabularyCategory(vocabulary.category)
        except ValueError:
            validation_result["is_valid"] = False
            validation_result["errors"].append(
                f"Invalid category: {vocabulary.category}"
            )

        # Check for duplicate terms
        if len(set(vocabulary.terms)) != len(vocabulary.terms):
            validation_result["warnings"].append("Duplicate terms found")

        # Check term format
        for term in vocabulary.terms:
            if not term.strip():
                validation_result["is_valid"] = False
                validation_result["errors"].append("Empty terms not allowed")
            elif len(term) > 100:
                validation_result["warnings"].append(
                    f"Term exceeds recommended length: {term}"
                )

        return validation_result
