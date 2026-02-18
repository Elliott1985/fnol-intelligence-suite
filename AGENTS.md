# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Commands

```bash
# Run the application
streamlit run fnol_intelligence_suite.py

# Install dependencies
pip install -r requirements.txt
```

## Architecture

Single-file Streamlit application (`fnol_intelligence_suite.py`) organized into sections:

1. **Configuration** (lines 20-42): Constants for policy dates, loss types, state-adjuster mappings, and Gemini API setup
2. **Helper Functions** (lines 45-169): Business logic including `generate_claim_id()`, `validate_policy_date()`, `get_adjuster_info()`, and `analyze_claim_with_ai()`
3. **Streamlit UI** (lines 172-763): CSS injection, sidebar, form, receipt, and emergency alert rendering

## AI Integration

The `analyze_claim_with_ai()` function uses `st.status()` for real-time progress updates and sends structured prompts to Gemini 2.0 Flash. Parses line-prefixed responses (RISK_LEVEL:, RISK_FLAGS:, SUBROGATION_POTENTIAL:, ALE_ALERT:, SUMMARY:). Uploaded images are passed as multimodal content via PIL.

## Key Configuration Points

- `POLICY_START_DATE` / `POLICY_END_DATE`: Coverage period validation (2026)
- `STATE_ADJUSTER_MAP`: Routes claims to licensed adjusters by state (GA, FL, TX, AL)
- `LOSS_TYPES`: Dropdown options for claim categorization
- `GOOGLE_API_KEY`: Required in `.env` for AI triage functionality
- `.streamlit/config.toml`: Theme configuration (Enterprise Light)

## Styling

Enterprise Light theme configured via `.streamlit/config.toml`. Custom CSS injected via `inject_custom_css()` hides Streamlit header/footer and adds box-shadows to containers. Card-based layout uses `st.container(border=True)`.
