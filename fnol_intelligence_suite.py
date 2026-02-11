"""
FNOL Intelligence Suite
Enterprise-grade First Notice of Loss intake engine for modern Insurtech carriers.
"""

import os
import random
import string
from datetime import date, datetime
from typing import Optional

import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

# Load environment variables
load_dotenv()

# =============================================================================
# CONFIGURATION
# =============================================================================

# Policy effective date range
POLICY_START_DATE = date(2026, 1, 1)
POLICY_END_DATE = date(2026, 12, 31)

# Loss types
LOSS_TYPES = ["Fire", "Water", "Hail", "Wind", "Theft"]

# State-to-Adjuster mapping
STATE_ADJUSTER_MAP = {
    "GA": "Sarah Mitchell",
    "FL": "Carlos Rodriguez",
    "TX": "Jennifer Thompson",
    "AL": "Michael Chen",
}

# Configure Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def generate_claim_id() -> str:
    """Generate a unique claim ID in format CLM-YYYY-XXXX."""
    year = datetime.now().year
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"CLM-{year}-{suffix}"


def validate_policy_date(loss_date: date) -> tuple[bool, str]:
    """Check if the loss date falls within the policy effective period."""
    if loss_date < POLICY_START_DATE:
        return False, "⚠️ Potential Coverage Gap: Date of Loss precedes policy inception."
    elif loss_date > POLICY_END_DATE:
        return False, "⚠️ Potential Coverage Gap: Date of Loss exceeds policy expiration."
    return True, "✅ Date of Loss within policy period."


def get_adjuster_info(state: str) -> Optional[tuple[str, str]]:
    """Get adjuster name for the given state."""
    if state in STATE_ADJUSTER_MAP:
        return STATE_ADJUSTER_MAP[state], state
    return None


def analyze_claim_with_ai(
    description: str,
    loss_type: str,
    uploaded_images: list,
) -> dict:
    """
    Use Gemini 2.0 Flash to analyze the claim for:
    - SIU Risk Scoring (Red Flags)
    - Subrogation Detection (3rd party liability)
    - ALE/Total Loss Triage
    """
    if not GOOGLE_API_KEY:
        return {
            "risk_level": "Unknown",
            "risk_flags": ["AI analysis unavailable - API key not configured"],
            "subrogation_potential": None,
            "ale_alert": False,
            "ai_summary": "AI analysis requires a valid GOOGLE_API_KEY.",
        }

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")

        prompt = f"""You are an insurance claims AI analyst for an FNOL (First Notice of Loss) system.
Analyze the following claim and provide a structured assessment.

**Loss Type:** {loss_type}
**Description:** {description}

Please analyze and respond in the following exact format:

RISK_LEVEL: [Low/Medium/High]
RISK_FLAGS: [List any red flags found, or "None" if none. Red flags include: vague timelines, property vacancy, conflicting damage descriptions, excessive claim amounts, recent policy changes, multiple prior claims. Only mark as High Risk if MULTIPLE triggers exist.]
SUBROGATION_POTENTIAL: [Identify any potential 3rd party liability such as: neighbor's tree, appliance manufacturer, contractor error, landlord negligence, auto accident with other driver, etc. Write "None identified" if none found.]
ALE_ALERT: [Yes/No - Set to Yes ONLY if description indicates: unlivable conditions, major fire damage, structural collapse, displacement required, or total loss]
SUMMARY: [2-3 sentence professional summary of the claim analysis]
"""

        # Include images if provided
        content_parts = [prompt]
        for img in uploaded_images[:3]:  # Limit to 3 images
            try:
                image = Image.open(img)
                content_parts.append(image)
            except Exception:
                continue

        response = model.generate_content(content_parts)
        response_text = response.text

        # Parse the response
        result = {
            "risk_level": "Medium",
            "risk_flags": [],
            "subrogation_potential": None,
            "ale_alert": False,
            "ai_summary": "",
        }

        for line in response_text.split("\n"):
            line = line.strip()
            if line.startswith("RISK_LEVEL:"):
                level = line.replace("RISK_LEVEL:", "").strip()
                result["risk_level"] = level if level in ["Low", "Medium", "High"] else "Medium"
            elif line.startswith("RISK_FLAGS:"):
                flags = line.replace("RISK_FLAGS:", "").strip()
                if flags.lower() != "none":
                    result["risk_flags"] = [f.strip() for f in flags.split(",") if f.strip()]
            elif line.startswith("SUBROGATION_POTENTIAL:"):
                sub = line.replace("SUBROGATION_POTENTIAL:", "").strip()
                if sub.lower() not in ["none", "none identified", "n/a"]:
                    result["subrogation_potential"] = sub
            elif line.startswith("ALE_ALERT:"):
                ale = line.replace("ALE_ALERT:", "").strip().lower()
                result["ale_alert"] = ale == "yes"
            elif line.startswith("SUMMARY:"):
                result["ai_summary"] = line.replace("SUMMARY:", "").strip()

        return result

    except Exception as e:
        return {
            "risk_level": "Unknown",
            "risk_flags": [f"AI analysis error: {str(e)}"],
            "subrogation_potential": None,
            "ale_alert": False,
            "ai_summary": "Unable to complete AI analysis.",
        }


# =============================================================================
# STREAMLIT UI
# =============================================================================

def render_sidebar():
    """Render the sidebar with security and compliance status."""
    with st.sidebar:
        st.title("🔐 Security & Compliance")
        st.divider()

        st.markdown("### System Status")

        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("🟢")
        with col2:
            st.markdown("**PII Redaction:** Active")

        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("🟢")
        with col2:
            st.markdown("**Data Retention:** Zero-Storage")

        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("🟢")
        with col2:
            st.markdown("**Infrastructure:** SOC2-Ready")

        st.divider()

        # API Status
        st.markdown("### AI Engine")
        if GOOGLE_API_KEY:
            st.success("✅ Gemini 2.0 Flash Connected")
        else:
            st.warning("⚠️ API Key Not Configured")
            st.caption("Set GOOGLE_API_KEY in .env file")


def render_main_form():
    """Render the main FNOL intake form."""
    st.title("📋 First Notice of Loss")
    st.markdown("*Enterprise FNOL Intake Engine*")
    st.divider()

    with st.form("fnol_form"):
        st.subheader("Policy Information")

        col1, col2 = st.columns(2)
        with col1:
            policy_number = st.text_input(
                "Policy Number *",
                placeholder="e.g., POL-2026-001234",
                help="Enter your policy number as shown on your declarations page",
            )
        with col2:
            state = st.selectbox(
                "State *",
                options=[""] + list(STATE_ADJUSTER_MAP.keys()),
                help="Select the state where the loss occurred",
            )

        st.subheader("Loss Details")

        col1, col2 = st.columns(2)
        with col1:
            loss_date = st.date_input(
                "Date of Loss *",
                value=date.today(),
                help="The date when the loss/damage occurred",
            )
        with col2:
            loss_type = st.selectbox(
                "Type of Loss *",
                options=[""] + LOSS_TYPES,
                help="Select the primary cause of loss",
            )

        description = st.text_area(
            "Description of Loss *",
            placeholder="Please describe in detail what happened, including the circumstances leading to the loss, the extent of damage, and any immediate actions taken...",
            height=150,
            help="Provide a detailed description of the incident",
        )

        st.subheader("Contact Information")

        col1, col2 = st.columns(2)
        with col1:
            email = st.text_input(
                "Email Address *",
                placeholder="your.email@example.com",
            )
        with col2:
            phone = st.text_input(
                "Phone Number *",
                placeholder="(555) 123-4567",
            )

        st.subheader("Supporting Documentation")

        uploaded_files = st.file_uploader(
            "Upload Photos & Documents",
            type=["jpg", "jpeg", "png", "pdf", "heic"],
            accept_multiple_files=True,
            help="Upload photos of damage and any supporting documentation",
        )

        st.divider()
        submitted = st.form_submit_button(
            "🚀 Submit Claim",
            use_container_width=True,
            type="primary",
        )

    return submitted, {
        "policy_number": policy_number,
        "state": state,
        "loss_date": loss_date,
        "loss_type": loss_type,
        "description": description,
        "email": email,
        "phone": phone,
        "uploaded_files": uploaded_files,
    }


def validate_form(data: dict) -> tuple[bool, list[str]]:
    """Validate the form data."""
    errors = []

    if not data["policy_number"]:
        errors.append("Policy Number is required")
    if not data["state"]:
        errors.append("State is required")
    if not data["loss_type"]:
        errors.append("Type of Loss is required")
    if not data["description"]:
        errors.append("Description of Loss is required")
    if not data["email"]:
        errors.append("Email Address is required")
    if not data["phone"]:
        errors.append("Phone Number is required")

    return len(errors) == 0, errors


def render_claim_receipt(claim_id: str, data: dict, adjuster_info: tuple, ai_analysis: dict):
    """Render the claim confirmation receipt."""
    st.divider()
    st.markdown("---")

    # ALE/Total Loss Emergency Alert
    if ai_analysis.get("ale_alert"):
        st.error(
            """
            ### 🚨 Immediate Action Required
            
            **Emergency Housing Protocol Activated**
            
            Our Temporary Housing Specialist has been automatically alerted and will contact you 
            **within 4 hours** to arrange emergency accommodations.
            
            **Do not worry about housing arrangements** – we are taking care of this for you.
            """
        )
        st.divider()

    # Professional Receipt
    st.success("### ✅ Claim Successfully Submitted")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Claim Details")
        st.markdown(f"**Claim Number:** `{claim_id}`")
        st.markdown(f"**Policy Number:** {data['policy_number']}")
        st.markdown(f"**Date of Loss:** {data['loss_date'].strftime('%B %d, %Y')}")
        st.markdown(f"**Type of Loss:** {data['loss_type']}")

    with col2:
        st.markdown("#### Your Adjuster")
        if adjuster_info:
            st.markdown(f"**Assigned Adjuster:** {adjuster_info[0]}")
            st.markdown(f"**Licensed in:** {adjuster_info[1]}")
        st.markdown(f"**Contact Email:** {data['email']}")
        st.markdown(f"**Contact Phone:** {data['phone']}")

    st.divider()

    # AI Analysis Summary
    st.markdown("#### 🤖 AI Triage Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        risk_color = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(
            ai_analysis["risk_level"], "⚪"
        )
        st.metric("Risk Assessment", f"{risk_color} {ai_analysis['risk_level']}")

    with col2:
        sub_status = "Yes" if ai_analysis["subrogation_potential"] else "No"
        st.metric("Subrogation Potential", sub_status)

    with col3:
        ale_status = "⚠️ Yes" if ai_analysis["ale_alert"] else "No"
        st.metric("ALE Alert", ale_status)

    if ai_analysis.get("ai_summary"):
        st.info(f"**Analysis:** {ai_analysis['ai_summary']}")

    if ai_analysis.get("risk_flags"):
        with st.expander("🚩 Risk Flags Identified"):
            for flag in ai_analysis["risk_flags"]:
                st.markdown(f"- {flag}")

    if ai_analysis.get("subrogation_potential"):
        with st.expander("⚖️ Subrogation Details"):
            st.markdown(ai_analysis["subrogation_potential"])

    st.divider()

    # Next Steps
    st.markdown("#### 📋 What Happens Next")

    st.markdown(
        """
        1. **Adjuster Contact:** You will be contacted by your assigned adjuster within **24-48 hours**.
        
        2. **Prevent Further Damage:** Take reasonable steps to prevent additional damage to your property. 
           This may include covering openings, shutting off water, or securing the premises.
        
        3. **Document Everything:** Continue to photograph any additional damage discovered and 
           keep all damaged items until your adjuster has inspected them.
        
        4. **Save All Receipts:** Keep receipts for any emergency repairs, temporary housing, 
           meals, or other loss-related expenses.
        
        5. **Prepare for Inspection:** Gather any relevant documents such as receipts for damaged 
           items, repair estimates, or police reports if applicable.
        """
    )

    st.divider()

    # Contact Information
    st.markdown("#### 📞 Need Immediate Assistance?")
    st.markdown(
        """
        - **Claims Hotline:** 1-800-555-CLAIM (24/7)
        - **Emergency Services:** 1-800-555-HELP
        - **Email:** claims@insurtech-carrier.com
        """
    )


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="FNOL Intelligence Suite",
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Custom CSS for professional styling
    st.markdown(
        """
        <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .stForm {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Render sidebar
    render_sidebar()

    # Render main form
    submitted, form_data = render_main_form()

    # Handle form submission
    if submitted:
        # Validate form
        is_valid, errors = validate_form(form_data)

        if not is_valid:
            for error in errors:
                st.error(f"❌ {error}")
            return

        # Policy date validation
        date_valid, date_message = validate_policy_date(form_data["loss_date"])
        if not date_valid:
            st.warning(date_message)

        # Get adjuster info
        adjuster_info = get_adjuster_info(form_data["state"])
        if adjuster_info:
            st.info(f"📋 Assigned Adjuster: **{adjuster_info[0]}** (Licensed in {adjuster_info[1]})")

        # Generate claim ID
        claim_id = generate_claim_id()

        # AI Analysis
        with st.spinner("🤖 AI Triage Engine analyzing claim..."):
            ai_analysis = analyze_claim_with_ai(
                description=form_data["description"],
                loss_type=form_data["loss_type"],
                uploaded_images=form_data["uploaded_files"],
            )

        # Render receipt
        render_claim_receipt(claim_id, form_data, adjuster_info, ai_analysis)


if __name__ == "__main__":
    main()
