# vocabulary_manager.py

import yaml
from pathlib import Path
import logging
from typing import Any, Optional

from app.services.exceptions import ConfigurationError

logger = logging.getLogger(__name__)

class VocabularyManager:
    """Manages vocabularies."""

    def __init__(self, vocabularies_path: Path):
        self.vocabularies_path = vocabularies_path

    def list_vocabularies(self) -> list[str]:
        """List available vocabularies."""
        if not self.vocabularies_path.exists():
            logger.warning("Vocabularies directory not found.")
            return []
        return [d.name for d in self.vocabularies_path.iterdir() if d.is_dir() or d.suffix in [".yml", ".yaml"]]

    def create_vocabulary(self, vocab_name: str, accept_terms: list[str], reject_terms: list[str]) -> None:
        """Create a new vocabulary."""
        vocab_path = self.vocabularies_path / vocab_name
        if vocab_path.exists():
            raise FileExistsError(f"Vocabulary already exists: {vocab_name}")

        vocab_path.mkdir(parents=True, exist_ok=True)
        self.save_vocabulary(vocab_name, accept_terms, reject_terms)
        logger.info(f"Vocabulary created: {vocab_name}")

    def update_vocabulary(self, vocab_name: str, accept_terms: list[str], reject_terms: list[str]) -> None:
        """Update an existing vocabulary."""
        vocab_path = self.vocabularies_path / vocab_name
        if not vocab_path.exists():
            raise FileNotFoundError(f"Vocabulary not found: {vocab_name}")

        self.save_vocabulary(vocab_name, accept_terms, reject_terms)
        logger.info(f"Vocabulary updated: {vocab_name}")

    def delete_vocabulary(self, vocab_name: str) -> None:
        """Delete a vocabulary."""
        vocab_path = self.vocabularies_path / vocab_name
        if not vocab_path.exists():
            raise FileNotFoundError(f"Vocabulary not found: {vocab_name}")

        for file in vocab_path.glob("*"):
            file.unlink()
        vocab_path.rmdir()
        logger.info(f"Vocabulary deleted: {vocab_name}")

    def load_vocabulary(self, vocab_name: str) -> dict[str, list[str]]:
        """Load a vocabulary."""
        vocab_path = self.vocabularies_path / vocab_name / "vocab.yml"
        if not vocab_path.exists():
            raise FileNotFoundError(f"Vocabulary not found: {vocab_name}")

        with vocab_path.open() as file:
            vocab = yaml.safe_load(file)

        logger.info(f"Vocabulary loaded: {vocab_name}")
        return vocab

    def validate_vocabulary(self, vocab_name: str) -> bool:
        """Validate a vocabulary."""
        try:
            vocab = self.load_vocabulary(vocab_name)
            # Example validation: ensure 'accept' and 'reject' are present
            if 'accept' not in vocab or 'reject' not in vocab:
                logger.error(f"Vocabulary {vocab_name} must contain 'accept' and 'reject' sections")
                return False
            if not vocab['accept'] and not vocab['reject']:
                logger.error(f"Vocabulary {vocab_name} is empty")
                return False
            logger.info(f"Vocabulary validated: {vocab_name}")
            return True
        except Exception as e:
            logger.error(f"Validation failed for vocabulary {vocab_name}: {e}")
            return False

    def save_vocabulary(self, vocab_name: str, accept_terms: list[str], reject_terms: list[str]) -> None:
        """Save vocabulary terms to YAML files."""
        vocab_path = self.vocabularies_path / vocab_name
        vocab_file = vocab_path / "vocab.yml"

        vocab_data = {
            "accept": accept_terms,
            "reject": reject_terms
        }

        with vocab_file.open('w') as file:
            yaml.safe_dump(vocab_data, file)

        logger.info(f"Vocabulary saved: {vocab_name}")
