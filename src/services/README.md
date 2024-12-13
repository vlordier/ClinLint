# Services

This directory contains service layer implementations that handle business logic and interactions between different parts of the application.

## Structure

The services directory contains modules that:
- Implement core business logic
- Handle interactions between repositories and controllers
- Manage complex operations that span multiple domains
- Provide reusable functionality across the application

## Best Practices

When adding new services:
1. Keep services focused on a single responsibility
2. Use dependency injection for external dependencies
3. Write unit tests for service logic
4. Document public interfaces and important implementation details
5. Handle errors appropriately and provide meaningful error messages

## Available Services

### `vale_runner.py`
- **Function**: Runs Vale linting on provided text.
- **Method**: `run_vale_on_text(text: str, config_path: str) -> list`

### `response_merger.py`
- **Function**: Merges Vale results and LLM feedback into a single response.
- **Method**: `merge_responses(vale_results, llm_feedback) -> dict`

### `config_loader.py`
- **Class**: `ConfigLoader`
- **Methods**:
  - `get_vale_config()`
  - `get_llm_config()`
  - `get_prompt_dir()`

### `batch_processor.py`
- **Class**: `BatchProcessor`
- **Methods**:
  - `process_batch(texts, llm_template: str) -> list`

### `llm_judge.py`
- **Class**: `LLMJudge`
- **Methods**:
  - `get_feedback(text: str, prompt_template: str, **kwargs) -> dict`
  - `load_prompt(template_name: str) -> PromptTemplate`
