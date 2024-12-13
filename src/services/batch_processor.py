from concurrent.futures import ThreadPoolExecutor
from services.suggestion_chain import SuggestionChain

class BatchProcessor:
    """
    Processes multiple texts in a batch for Vale and LLM-based suggestions.
    """

    def __init__(self, vale_config: str, llm_judge):
        self.vale_config = vale_config
        self.llm_judge = llm_judge

    def process_batch(self, texts, llm_template: str):
        """
        Processes a batch of texts and generates suggestions.

        Args:
            texts (list): List of input texts.
            llm_template (str): LLM prompt template for suggestions.

        Returns:
            list: Results for each text.
        """
        results = []

        def process_single(text):
            suggestion_chain = SuggestionChain(self.vale_config, self.llm_judge)
            return suggestion_chain.generate_suggestions(text, llm_template)

        with ThreadPoolExecutor() as executor:
            results = list(executor.map(process_single, texts))

        return results
