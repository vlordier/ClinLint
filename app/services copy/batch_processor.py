"""Module for batch processing of multiple texts for Vale and LLM-based suggestions."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from typing import Optional

from app.services.custom_types import SuggestionResult
from app.services.llm_feedback import LLMFeedback
from app.services.suggestion_chain import ChainConfig, SuggestionChain


class BatchProcessor:
    """Processes multiple texts in a batch for Vale and LLM-based suggestions.

    Thread-safe batch processing of multiple texts.
    """

    def __init__(self, vale_config: str, llm_feedback: LLMFeedback) -> None:
        """Initializes the BatchProcessor.

        Args:
            vale_config (str): Vale configuration.
            llm_feedback (LLMFeedback): LLM-based suggestion generator.
        """
        self.vale_config = vale_config
        self.llm_feedback = llm_feedback
        self._lock = Lock()

    def process_batch(
        self,
        texts: list[str],
        config: ChainConfig,
        max_workers: Optional[int] = None,
        timeout: Optional[int] = None
    ) -> list[SuggestionResult]:
        """Processes a batch of texts and generates suggestions."""
        self._validate_inputs(texts, config)
        results, errors = self._initialize_results(texts)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {
                executor.submit(self._process_single, i, text, config, results, errors): i
                for i, text in enumerate(texts)
            }
            self._handle_futures(future_to_index, timeout)

        self._check_for_errors(errors)
        return results

    def _validate_inputs(self, texts: list[str], config: ChainConfig) -> None:
        if texts is None or not isinstance(texts, list):
            raise ValueError("texts must be a non-None list")
        if not texts:
            raise ValueError("texts must be a non-empty list")
        if config is None:
            raise TypeError("config cannot be None")

    def _initialize_results(self, texts: list[str]) -> tuple[list[Optional[SuggestionResult]], list[tuple[int, str]]]:
        results = [None] * len(texts)
        errors = []
        return results, errors

    def _process_single(self, index: int, text: str, config: ChainConfig, results: list[Optional[SuggestionResult]], errors: list[tuple[int, str]]) -> None:
        try:
            chain = self._get_thread_chain()
            result = chain.generate_suggestions(text, config=config)
            with self._lock:
                results[index] = result
        except Exception as e:
            with self._lock:
                errors.append((index, str(e)))
                results[index] = None
            raise

    def _get_thread_chain(self) -> SuggestionChain:
        import threading
        thread_local = threading.local()
        if not hasattr(thread_local, 'suggestion_chain'):
            thread_local.suggestion_chain = SuggestionChain(
                self.vale_config,
                self.llm_feedback
            )
        return thread_local.suggestion_chain

    def _handle_futures(self, future_to_index: dict, timeout: Optional[int]) -> None:
        try:
            for future in as_completed(future_to_index.keys(), timeout=timeout):
                future.result()
        except TimeoutError:
            for future in future_to_index:
                future.cancel()
            raise TimeoutError(f"Batch processing timed out after {timeout} seconds") from None

    def _check_for_errors(self, errors: list[tuple[int, str]]) -> None:
        if errors:
            error_msg = "; ".join(f"Text {idx}: {err}" for idx, err in errors)
            raise RuntimeError(f"Batch processing failed: {error_msg}")
