import pytest

from services.suggestion_chain import AnalysisMode, ChainConfig, SuggestionChain


@pytest.fixture
def mock_llm_judge(mocker) -> object:
    from services.llm_judge import LLMJudge

    class MockLLMJudge(LLMJudge):
        def get_feedback(self, prompt_template, **kwargs) -> dict:
            if "generic_prompt" in prompt_template:
                return {"feedback": ["Improve clarity and precision"]}
            elif "improvement_prompt" in prompt_template:
                return {"feedback": ["Replace vague terms with specific metrics"]}
            return {"feedback": ["Default feedback"]}
    mock_config_loader = mocker.MagicMock()
    mock_config_loader.get_llm_config.return_value = {
        "openai": {
            "api_key": "test_api_key",
            "model": "test_model",
            "temperature": 0.5,
            "max_tokens": 100
        }
    }
    return MockLLMJudge(version="v1", config_loader=mock_config_loader)

@pytest.mark.parametrize("text, expected_issues", [
    ("The patient showed significant improvement.", ["CSR.Precision", "CSR.Consistency"]),
    ("Approximately 50% of subjects responded.", ["CSR.Precision"]),
    ("The results were not statistically significant.", ["CSR.Statistical"])
])
def test_vale_only_mode(mock_llm_judge, mocker, text, expected_issues) -> None:
    mock_vale_runner = mocker.patch("services.vale_runner.run_vale_on_text")
    mock_vale_runner.return_value = {
        "stdin.md": [{"Line": 1, "Message": "Use 'subject' instead of 'patient'", "Rule": "CSR.Precision"}]
    }
    chain = SuggestionChain("config/rules/final-template.ini", mock_llm_judge)
    config = ChainConfig(
        mode=AnalysisMode.VALE_ONLY,
        vale_rules=["CSR.Precision", "CSR.Consistency"]
    )

    result = chain.generate_suggestions(
        "The patient showed significant improvement.",
        config=ChainConfig(
            mode=AnalysisMode.VALE_ONLY,
            vale_rules=["CSR.Precision", "CSR.Consistency"],
            llm_templates=[]
        )
    )
    assert result is not None

def test_llm_only_mode(mock_llm_judge) -> None:
    chain = SuggestionChain("config/rules/final-template.ini", mock_llm_judge)
    config = ChainConfig(
        mode=AnalysisMode.LLM_ONLY,
        vale_rules=[],
        llm_templates=["generic_prompt", "improvement_prompt"]
    )

    result = chain.generate_suggestions(
        "The patient showed significant improvement.",
        ChainConfig(
            mode=AnalysisMode.LLM_ONLY,
            vale_rules=[],
            llm_templates=["generic_prompt", "improvement_prompt"]
        )
    )
    assert result is not None

@pytest.mark.parametrize("text, vale_rules, llm_templates", [
    ("The patient showed significant improvement.", ["CSR.Precision"], ["improvement_prompt"]),
    ("Approximately 50% of subjects responded.", ["CSR.Consistency"], ["generic_prompt"]),
    ("The results were not statistically significant.", ["CSR.Statistical"], ["csr_section_prompt"])
])
def test_combined_mode(mock_llm_judge, text, vale_rules, llm_templates) -> None:
    chain = SuggestionChain(".vale/styles/CSR/rules.yml", mock_llm_judge)
    config = ChainConfig(
        mode=AnalysisMode.COMBINED,
        vale_rules=["CSR.Precision"],
        llm_templates=["improvement_prompt"]
    )

    result = chain.generate_suggestions(
        "The patient showed significant improvement.",
        ChainConfig(mode=AnalysisMode.COMBINED, vale_rules=["CSR.Precision"], llm_templates=["improvement_prompt"])
    )
    assert result is not None

@pytest.mark.parametrize("text, section_name", [
    ("The treatment showed significant results (p>0.05).", "Statistical Analysis"),
    ("The study was conducted in accordance with GCP.", "Study Conduct"),
    ("The adverse events were mild and transient.", "Safety Reporting")
])
def test_section_specific_analysis(mock_llm_judge, text, section_name) -> None:
    chain = SuggestionChain(".vale/styles/CSR/rules.yml", mock_llm_judge)
    config = ChainConfig(
        mode=AnalysisMode.COMBINED,
        vale_rules=["CSR.Statistical"],
        llm_templates=["csr_section_prompt"],
        section_name="Statistical Analysis"
    )

    result = chain.generate_suggestions(
        "The treatment showed significant results (p>0.05).",
        ChainConfig(mode=AnalysisMode.COMBINED, vale_rules=["CSR.Statistical"], llm_templates=["csr_section_prompt"], section_name="Statistical Analysis")
    )
    assert result is not None
