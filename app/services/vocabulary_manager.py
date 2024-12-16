# vocabulary_manager.py

import yaml
from pathlib import Path
import logging
from typing import Any, Optional, TYPE_CHECKING

from app.services.exceptions import ConfigurationError
from app.schemas.vocabulary_schemas import Vocabulary, VocabularyTerms

if TYPE_CHECKING:
    from app.schemas.vocabulary_schemas import Vocabulary

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
        
        vocabularies = []
        for item in self.vocabularies_path.iterdir():
            if item.is_dir():
                # Add directory name and check for subdirectories
                for subdir in item.iterdir():
                    if subdir.is_dir():
                        vocabularies.append(f"{item.name}/{subdir.name}")        
        return vocabularies

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

    def load_vocabulary(self, vocab_path: str) -> "Vocabulary":
        """Load a vocabulary and return a Vocabulary object."""
        from app.schemas.vocabulary_schemas import Vocabulary, VocabularyTerms
        
        # Split path into components and ensure CSR is the base directory
        path_parts = vocab_path.split('/')
        if not path_parts[0] == 'CSR':
            path_parts.insert(0, 'CSR')
            
        # Build the full path including all components
        full_path = self.vocabularies_path
        for part in path_parts:
            full_path = full_path / part
        full_path = full_path / "vocab.yml"
        
        if not full_path.exists():
            raise FileNotFoundError(f"Vocabulary not found: {vocab_path}")

        with full_path.open() as file:
            vocab_data = yaml.safe_load(file)

        # Extract the vocabulary name from the path
        vocab_name = path_parts[-1]

        terms = VocabularyTerms(
            accept=vocab_data.get('accept', []),
            reject=vocab_data.get('reject', [])
        )

        return Vocabulary(
            name=vocab_name,
            terms=terms,
            description=vocab_data.get('description'),
            path=str(full_path)
        )

    def validate_vocabulary(self, vocab_name: str) -> bool:
        """Validate a vocabulary."""
        try:
            # Build the full path for validation
            path_parts = vocab_name.split('/')
            if not path_parts[0] == 'CSR':
                path_parts.insert(0, 'CSR')
                
            full_path = self.vocabularies_path
            for part in path_parts:
                full_path = full_path / part
            full_path = full_path / "vocab.yml"
            
            if not full_path.exists():
                logger.error(f"Vocabulary not found: {vocab_name}")
                return False
                
            vocab = self.load_vocabulary(vocab_name)
            if not vocab.terms.accept and not vocab.terms.reject:
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
