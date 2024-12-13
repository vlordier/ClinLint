import pytest

from services.suggestion_chain import AnalysisMode, ChainConfig, SuggestionChain


@pytest.fixture
def mock_llm_judge():
    class MockLLMJudge:
        def get_feedback(self, prompt_template, **kwargs):
            if "generic_prompt" in prompt_template:
                return {"feedback": ["Improve clarity and precision"]}
            elif "improvement_prompt" in prompt_template:
                return {"feedback": ["Replace vague terms with specific metrics"]}
            return {"feedback": ["Default feedback"]}
    return MockLLMJudge()

def test_vale_only_mode(mock_llm_judge):
    chain = SuggestionChain(".vale/styles/CSR/rules.yml", mock_llm_judge)
    config = ChainConfig(
        mode=AnalysisMode.VALE_ONLY,
        vale_rules=["CSR.Precision", "CSR.Consistency"]
    )

    result = chain.generate_suggestions(
        "The patient showed significant improvement.",
        ChainConfig(
            mode=AnalysisMode.VALE_ONLY,
            vale_rules=["CSR.Precision", "CSR.Consistency"],
            llm_templates=[]
        )
    )
    assert result is not None

def test_llm_only_mode(mock_llm_judge):
    chain = SuggestionChain(".vale/styles/CSR/rules.yml", mock_llm_judge)
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

def test_combined_mode(mock_llm_judge):
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

def test_section_specific_analysis(mock_llm_judge):
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
