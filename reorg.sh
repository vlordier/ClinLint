# General Writing Standards
mkdir -p .vale/styles/CSR/General_Writing_Standards/Spelling_and_Language_Usage
mkdir -p .vale/styles/CSR/General_Writing_Standards/Grammar_and_Style
mkdir -p .vale/styles/CSR/General_Writing_Standards/Readability_and_Clarity

mv .vale/styles/CSR/american_english/spelling.yml .vale/styles/CSR/General_Writing_Standards/Spelling_and_Language_Usage/
mv .vale/styles/CSR/american_english/punctuation.yml .vale/styles/CSR/General_Writing_Standards/Spelling_and_Language_Usage/
mv .vale/styles/CSR/formatting/capitalization.yml .vale/styles/CSR/General_Writing_Standards/Spelling_and_Language_Usage/
mv .vale/styles/CSR/formatting/titles.yml .vale/styles/CSR/General_Writing_Standards/Spelling_and_Language_Usage/

mv .vale/styles/CSR/scientific/verb_tense.yml .vale/styles/CSR/General_Writing_Standards/Grammar_and_Style/
mv .vale/styles/CSR/scientific/terminology.yml .vale/styles/CSR/General_Writing_Standards/Grammar_and_Style/
mv .vale/styles/CSR/scientific/precision.yml .vale/styles/CSR/General_Writing_Standards/Grammar_and_Style/
mv .vale/styles/CSR/quality/misspellings.yml .vale/styles/CSR/General_Writing_Standards/Grammar_and_Style/
mv .vale/styles/CSR/scientific/uncertainty_reporting.yml .vale/styles/CSR/General_Writing_Standards/Grammar_and_Style/

mv .vale/styles/CSR/readability/metrics.yml .vale/styles/CSR/General_Writing_Standards/Readability_and_Clarity/
mv .vale/styles/CSR/scientific/writing_style.yml .vale/styles/CSR/General_Writing_Standards/Readability_and_Clarity/
mv .vale/styles/CSR/quality/basic_consistency.yml .vale/styles/CSR/General_Writing_Standards/Readability_and_Clarity/

# Document Structure and Sections
mkdir -p .vale/styles/CSR/Document_Structure_and_Sections/Overall_Structure
mkdir -p .vale/styles/CSR/Document_Structure_and_Sections/Specific_Sections

mv .vale/styles/CSR/sections/*.yml .vale/styles/CSR/Document_Structure_and_Sections/Overall_Structure/
mv .vale/styles/CSR/quality/structure.yml .vale/styles/CSR/Document_Structure_and_Sections/Overall_Structure/
mv .vale/styles/CSR/regulatory/ich_e3_structure.yml .vale/styles/CSR/Document_Structure_and_Sections/Overall_Structure/
mv .vale/styles/CSR/formatting/structure.yml .vale/styles/CSR/Document_Structure_and_Sections/Overall_Structure/

mv .vale/styles/CSR/sections/synopsis.yml .vale/styles/CSR/Document_Structure_and_Sections/Specific_Sections/
mv .vale/styles/CSR/sections/introduction.yml .vale/styles/CSR/Document_Structure_and_Sections/Specific_Sections/
mv .vale/styles/CSR/sections/methods.yml .vale/styles/CSR/Document_Structure_and_Sections/Specific_Sections/
mv .vale/styles/CSR/study_design/methodology.yml .vale/styles/CSR/Document_Structure_and_Sections/Specific_Sections/
mv .vale/styles/CSR/sections/results.yml .vale/styles/CSR/Document_Structure_and_Sections/Specific_Sections/
mv .vale/styles/CSR/endpoints/comprehensive_reporting.yml .vale/styles/CSR/Document_Structure_and_Sections/Specific_Sections/
mv .vale/styles/CSR/sections/discussion.yml .vale/styles/CSR/Document_Structure_and_Sections/Specific_Sections/
mv .vale/styles/CSR/sections/conclusions.yml .vale/styles/CSR/Document_Structure_and_Sections/Specific_Sections/

# Efficacy Reporting
mkdir -p .vale/styles/CSR/Efficacy_Reporting/Endpoints_and_Outcomes
mkdir -p .vale/styles/CSR/Efficacy_Reporting/Special_Considerations

mv .vale/styles/CSR/packages/core/efficacy/endpoints.yml .vale/styles/CSR/Efficacy_Reporting/Endpoints_and_Outcomes/
mv .vale/styles/CSR/endpoints/precision.yml .vale/styles/CSR/Efficacy_Reporting/Endpoints_and_Outcomes/
mv .vale/styles/CSR/statistics/reporting.yml .vale/styles/CSR/Efficacy_Reporting/Endpoints_and_Outcomes/
mv .vale/styles/CSR/statistics/terminology.yml .vale/styles/CSR/Efficacy_Reporting/Endpoints_and_Outcomes/
mv .vale/styles/CSR/statistics/unified_statistics.yml .vale/styles/CSR/Efficacy_Reporting/Endpoints_and_Outcomes/

mv .vale/styles/CSR/statistical/estimands.yml .vale/styles/CSR/Efficacy_Reporting/Special_Considerations/
mv .vale/styles/CSR/statistics/population.yml .vale/styles/CSR/Efficacy_Reporting/Special_Considerations/

# Safety Reporting
mkdir -p .vale/styles/CSR/Safety_Reporting/Adverse_Events
mkdir -p .vale/styles/CSR/Safety_Reporting/Safety_Monitoring

mv .vale/styles/CSR/safety/adverse_events.yml .vale/styles/CSR/Safety_Reporting/Adverse_Events/
mv .vale/styles/CSR/safety/severity.yml .vale/styles/CSR/Safety_Reporting/Adverse_Events/
mv .vale/styles/CSR/safety/causality.yml .vale/styles/CSR/Safety_Reporting/Adverse_Events/
mv .vale/styles/CSR/safety/safety_reporting.yml .vale/styles/CSR/Safety_Reporting/Adverse_Events/

mv .vale/styles/CSR/laboratory/reporting.yml .vale/styles/CSR/Safety_Reporting/Safety_Monitoring/
mv .vale/styles/CSR/packages/core/safety/laboratory.yml .vale/styles/CSR/Safety_Reporting/Safety_Monitoring/
mv .vale/styles/CSR/packages/core/safety/unified_safety.yml .vale/styles/CSR/Safety_Reporting/Safety_Monitoring/
mv .vale/styles/CSR/cardiovascular/cardiac_safety.yml .vale/styles/CSR/Safety_Reporting/Safety_Monitoring/

# Regulatory Compliance
mkdir -p .vale/styles/CSR/Regulatory_Compliance/ICH_Guidelines
mkdir -p .vale/styles/CSR/Regulatory_Compliance/Regional_Requirements
mkdir -p .vale/styles/CSR/Regulatory_Compliance/Good_Clinical_Practice

mv .vale/styles/CSR/regulatory/ich_e3_structure.yml .vale/styles/CSR/Regulatory_Compliance/ICH_Guidelines/
mv .vale/styles/CSR/regulatory/ich_e3_content.yml .vale/styles/CSR/Regulatory_Compliance/ICH_Guidelines/

mv .vale/styles/CSR/regulatory/regional_specific.yml .vale/styles/CSR/Regulatory_Compliance/Regional_Requirements/
mv .vale/styles/CSR/regulatory/regional_requirements.yml .vale/styles/CSR/Regulatory_Compliance/Regional_Requirements/

mv .vale/styles/CSR/study_types/special/gcp_requirements.yml .vale/styles/CSR/Regulatory_Compliance/Good_Clinical_Practice/

# Statistical Considerations
mkdir -p .vale/styles/CSR/Statistical_Considerations/Methodology
mkdir -p .vale/styles/CSR/Statistical_Considerations/Terminology_and_Precision

mv .vale/styles/CSR/statistical_methods.yml .vale/styles/CSR/Statistical_Considerations/Methodology/
mv .vale/styles/CSR/statistics/advanced_methods.yml .vale/styles/CSR/Statistical_Considerations/Methodology/

mv .vale/styles/CSR/statistics/terminology.yml .vale/styles/CSR/Statistical_Considerations/Terminology_and_Precision/
mv .vale/styles/CSR/endpoints/precision.yml .vale/styles/CSR/Statistical_Considerations/Terminology_and_Precision/

# Data Quality and Integrity
mkdir -p .vale/styles/CSR/Data_Quality_and_Integrity/Data_Standards_and_Management
mkdir -p .vale/styles/CSR/Data_Quality_and_Integrity/Version_Control_and_Documentation

mv .vale/styles/CSR/clinical_documentation/data_standards.yml .vale/styles/CSR/Data_Quality_and_Integrity/Data_Standards_and_Management/
mv .vale/styles/CSR/quality/data_integrity.yml .vale/styles/CSR/Data_Quality_and_Integrity/Data_Standards_and_Management/

mv .vale/styles/CSR/metadata/requirements.yml .vale/styles/CSR/Data_Quality_and_Integrity/Version_Control_and_Documentation/

# Therapeutic Area-Specific Guidelines
mkdir -p .vale/styles/CSR/Therapeutic_Area_Specific_Guidelines/Oncology
mkdir -p .vale/styles/CSR/Therapeutic_Area_Specific_Guidelines/Immunology
mkdir -p .vale/styles/CSR/Therapeutic_Area_Specific_Guidelines/Other_Areas

mv .vale/styles/CSR/oncology/response_criteria.yml .vale/styles/CSR/Therapeutic_Area_Specific_Guidelines/Oncology/
mv .vale/styles/CSR/biomarkers/analysis_requirements.yml .vale/styles/CSR/Therapeutic_Area_Specific_Guidelines/Oncology/

mv .vale/styles/CSR/immunology/advanced_monitoring.yml .vale/styles/CSR/Therapeutic_Area_Specific_Guidelines/Immunology/

mv .vale/styles/CSR/other/pediatric.yml .vale/styles/CSR/Therapeutic_Area_Specific_Guidelines/Other_Areas/
mv .vale/styles/CSR/study_types/rare_disease/requirements.yml .vale/styles/CSR/Therapeutic_Area_Specific_Guidelines/Other_Areas/

# Study Phase-Specific Requirements
mkdir -p .vale/styles/CSR/Study_Phase_Specific_Requirements/Phase_I
mkdir -p .vale/styles/CSR/Study_Phase_Specific_Requirements/Phase_II
mkdir -p .vale/styles/CSR/Study_Phase_Specific_Requirements/Phase_III
mkdir -p .vale/styles/CSR/Study_Phase_Specific_Requirements/Phase_IV

mv .vale/styles/CSR/phase1/first_in_human.yml .vale/styles/CSR/Study_Phase_Specific_Requirements/Phase_I/
mv .vale/styles/CSR/packages/phase1/pk_pd.yml .vale/styles/CSR/Study_Phase_Specific_Requirements/Phase_I/

mv .vale/styles/CSR/packages/phase2/efficacy.yml .vale/styles/CSR/Study_Phase_Specific_Requirements/Phase_II/
mv .vale/styles/CSR/packages/phase2/pk_pd.yml .vale/styles/CSR/Study_Phase_Specific_Requirements/Phase_II/

mv .vale/styles/CSR/packages/phase3/efficacy_requirements.yml .vale/styles/CSR/Study_Phase_Specific_Requirements/Phase_III/
mv .vale/styles/CSR/phase3/pivotal_trial.yml .vale/styles/CSR/Study_Phase_Specific_Requirements/Phase_III/

mv .vale/styles/CSR/packages/phase4/safety.yml .vale/styles/CSR/Study_Phase_Specific_Requirements/Phase_IV/
mv .vale/styles/CSR/packages/phase4/efficacy_requirements.yml .vale/styles/CSR/Study_Phase_Specific_Requirements/Phase_IV/

# Appendices and Supplemental Information
mkdir -p .vale/styles/CSR/Appendices_and_Supplemental_Information/Tables_and_Figures
mkdir -p .vale/styles/CSR/Appendices_and_Supplemental_Information/Examples_and_Case_Studies

mv .vale/styles/CSR/formatting/tables.yml .vale/styles/CSR/Appendices_and_Supplemental_Information/Tables_and_Figures/
mv .vale/styles/CSR/quality/cross_references.yml .vale/styles/CSR/Appendices_and_Supplemental_Information/Tables_and_Figures/

mv .vale/styles/CSR/examples/*.yml .vale/styles/CSR/Appendices_and_Supplemental_Information/Examples_and_Case_Studies/

# Packages Directory
mkdir -p .vale/packages/CSR/Core
mkdir -p .vale/packages/CSR/Phase_Specific
mkdir -p .vale/packages/CSR/Therapeutic_Area_Specific
mkdir -p .vale/packages/CSR/Supplementary
