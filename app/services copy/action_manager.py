# action_manager.py

from pathlib import Path
import logging

from app.services.exceptions import ConfigurationError

logger = logging.getLogger(__name__)

class ActionManager:
    """Manages action scripts."""

    def __init__(self, actions_path: Path):
        self.actions_path = actions_path

    def list_actions(self) -> list[str]:
        """List available actions."""
        if not self.actions_path.exists():
            logger.warning("Actions directory not found.")
            return []
        return [f.stem for f in self.actions_path.glob("*.tengo")]

    def create_action(self, action_name: str, script_content: str) -> None:
        """Create a new action script."""
        action_path = self.actions_path / f"{action_name}.tengo"
        if action_path.exists():
            raise FileExistsError(f"Action script already exists: {action_name}")

        action_path.write_text(script_content)
        logger.info(f"Action script created: {action_name}")

    def update_action(self, action_name: str, script_content: str) -> None:
        """Update an existing action script."""
        action_path = self.actions_path / f"{action_name}.tengo"
        if not action_path.exists():
            raise FileNotFoundError(f"Action script not found: {action_name}")

        action_path.write_text(script_content)
        logger.info(f"Action script updated: {action_name}")

    def delete_action(self, action_name: str) -> None:
        """Delete an action script."""
        action_path = self.actions_path / f"{action_name}.tengo"
        if not action_path.exists():
            raise FileNotFoundError(f"Action script not found: {action_name}")

        action_path.unlink()
        logger.info(f"Action script deleted: {action_name}")

    def load_action(self, action_name: str) -> str:
        """Load an action script."""
        action_path = self.actions_path / f"{action_name}.tengo"
        if not action_path.exists():
            raise FileNotFoundError(f"Action script not found: {action_name}")

        script_content = action_path.read_text()
        logger.info(f"Action script loaded: {action_name}")
        return script_content

    def validate_action(self, action_name: str) -> bool:
        """Validate an action script."""
        try:
            script_content = self.load_action(action_name)
            # Add validation logic here, e.g., syntax check
            # For example, ensure it contains certain keywords or follows a pattern
            if not script_content.strip():
                logger.error(f"Action script {action_name} is empty")
                return False
            logger.info(f"Action script validated: {action_name}")
            return True
        except Exception as e:
            logger.error(f"Validation failed for action script {action_name}: {e}")
            return False
