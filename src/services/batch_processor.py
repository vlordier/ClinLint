"""Module for batch processing of multiple texts for Vale and LLM-based suggestions."""

from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from services.custom_types import SuggestionResult
from services.llm_judge import LLMJudge
from services.suggestion_chain import SuggestionChain


class BatchProcessor:
    """Processes multiple texts in a batch for Vale and LLM-based suggestions.

    Thread-safe batch processing of multiple texts.
    """

    def __init__(self, vale_config: str, llm_judge: LLMJudge) -> None:
        """Initializes the BatchProcessor.

        Args:
            vale_config (str): Vale configuration.
            llm_judge (LLMJudge): LLM-based suggestion generator.
        """
        self.vale_config = vale_config
        self.llm_judge = llm_judge
        self._lock = Lock()

    def process_batch(
        self, texts: list[str], llm_template: str
    ) -> list[SuggestionResult]:
        """Processes a batch of texts and generates suggestions.

        Args:
            texts (list): List of input texts.
            llm_template (str): LLM prompt template for suggestions.

        Returns:
            list: Results for each text.
        """
        results = []

        def process_single(text: str) -> SuggestionResult:
            """Processes a single text and generates suggestions.

            Args:
                text (str): Input text.

            Returns:
                SuggestionResult: Suggestions for the input text.
            """
            suggestion_chain = SuggestionChain(self.vale_config, self.llm_judge)
            return suggestion_chain.generate_suggestions(text, llm_template)

        with ThreadPoolExecutor() as executor:
            results = list(executor.map(process_single, texts))

        return results
