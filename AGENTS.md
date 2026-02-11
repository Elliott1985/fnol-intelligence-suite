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

Single-file Streamlit application (`fnol_intelligence_suite.py`) organized into three sections:

1. **Configuration** (lines 20-42): Constants for policy dates, loss types, state-adjuster mappings, and Gemini API setup
2. **Helper Functions** (lines 45-159): Business logic including `generate_claim_id()`, `validate_policy_date()`, `get_adjuster_info()`, and `analyze_claim_with_ai()`
3. **Streamlit UI** (lines 162-490): Rendering functions for sidebar, form, and receipt components

## AI Integration

The `analyze_claim_with_ai()` function sends structured prompts to Gemini 2.0 Flash and parses line-prefixed responses (RISK_LEVEL:, RISK_FLAGS:, SUBROGATION_POTENTIAL:, ALE_ALERT:, SUMMARY:). Uploaded images are passed as multimodal content via PIL.

## Key Configuration Points

- `POLICY_START_DATE` / `POLICY_END_DATE`: Coverage period validation
- `STATE_ADJUSTER_MAP`: Routes claims to licensed adjusters by state
- `LOSS_TYPES`: Dropdown options for claim categorization
- `GOOGLE_API_KEY`: Required in `.env` for AI triage functionality

## Styling

Custom CSS is injected via `st.markdown()` with `unsafe_allow_html=True` in the `main()` function. UI follows enterprise SaaS patterns with sidebar status indicators and form-based intake.
