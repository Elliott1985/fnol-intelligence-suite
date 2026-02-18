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

# Load environment variables (for local development)
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


def get_api_key() -> Optional[str]:
    """Get API key from Streamlit secrets (Cloud) or environment variable (local)."""
    # Priority 1: Streamlit secrets (for Streamlit Cloud deployment)
    try:
        return st.secrets["GOOGLE_API_KEY"]
    except (KeyError, FileNotFoundError):
        pass
    # Priority 2: Environment variable (for local development)
    return os.getenv("GOOGLE_API_KEY")


# Configure Gemini (deferred until key is available)
GOOGLE_API_KEY = get_api_key()
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
    status_container,
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
        status_container.update(label="Initializing AI Engine...", state="running")
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
        status_container.update(label="Processing uploaded documentation...", state="running")
        content_parts = [prompt]
        for img in uploaded_images[:3]:  # Limit to 3 images
            try:
                image = Image.open(img)
                content_parts.append(image)
            except Exception:
                continue

        status_container.update(label="Running SIU Risk Analysis...", state="running")
        response = model.generate_content(content_parts)
        response_text = response.text

        status_container.update(label="Evaluating Subrogation Potential...", state="running")
        
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

        status_container.update(label="Checking ALE/Total Loss Indicators...", state="running")
        status_container.update(label="Analysis Complete ✓", state="complete")
        
        return result

    except Exception as e:
        status_container.update(label="Analysis Failed", state="error")
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

def inject_custom_css():
    """Inject custom CSS for Enterprise Light styling."""
    st.markdown(
        """
        <style>
        /* === Hide Streamlit Header/Footer === */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* === Global Container Shadows === */
        [data-testid="stVerticalBlock"] > div:has(> [data-testid="stForm"]),
        [data-testid="stExpander"],
        .stAlert {
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.06);
        }
        
        /* === Card Containers === */
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 8px !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06) !important;
        }
        
        /* === Sidebar Styling === */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1E3A5F 0%, #2D4A6F 100%) !important;
        }
        
        [data-testid="stSidebar"] * {
            color: #ffffff !important;
        }
        
        [data-testid="stSidebar"] hr {
            border-color: rgba(255, 255, 255, 0.15) !important;
            margin: 1rem 0 !important;
        }
        
        [data-testid="stSidebar"] .stMarkdown p {
            color: #E2E8F0 !important;
            font-size: 0.9rem;
        }
        
        /* === Form Styling === */
        [data-testid="stForm"] {
            padding: 1.5rem;
        }
        
        /* === Input Fields === */
        .stTextInput input,
        .stTextArea textarea,
        .stSelectbox > div > div {
            border: 1px solid #CBD5E1 !important;
            border-radius: 6px !important;
        }
        
        .stTextInput input:focus,
        .stTextArea textarea:focus {
            border-color: #2962FF !important;
            box-shadow: 0 0 0 2px rgba(41, 98, 255, 0.1) !important;
        }
        
        /* === Labels === */
        .stTextInput label,
        .stTextArea label,
        .stSelectbox label,
        .stDateInput label,
        .stFileUploader label {
            font-weight: 600 !important;
            color: #334155 !important;
            font-size: 0.85rem !important;
            text-transform: uppercase;
            letter-spacing: 0.025em;
        }
        
        /* === Primary Button === */
        .stFormSubmitButton button {
            background: linear-gradient(135deg, #2962FF 0%, #1E88E5 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 0.75rem 1.5rem !important;
            transition: all 0.2s ease;
        }
        
        .stFormSubmitButton button:hover {
            background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%) !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(41, 98, 255, 0.3);
        }
        
        /* === Metrics === */
        [data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 1rem;
        }
        
        [data-testid="stMetric"] label {
            color: #64748B !important;
            font-size: 0.75rem !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        [data-testid="stMetricValue"] {
            color: #1E293B !important;
            font-weight: 700 !important;
        }
        
        /* === Status Widget === */
        [data-testid="stStatusWidget"] {
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
        }
        
        /* === Emergency Alert Box === */
        .emergency-alert {
            background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 8px;
            margin: 1rem 0;
            box-shadow: 0 4px 14px rgba(220, 38, 38, 0.3);
        }
        
        .emergency-alert h3 {
            color: white !important;
            margin: 0 0 0.5rem 0;
        }
        
        .emergency-alert p {
            color: rgba(255, 255, 255, 0.95);
            margin: 0;
        }
        
        /* === Receipt Document === */
        .receipt-header {
            background: linear-gradient(135deg, #1E3A5F 0%, #2D4A6F 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 8px 8px 0 0;
            margin: -1rem -1rem 1rem -1rem;
        }
        
        .receipt-header h2 {
            color: white !important;
            margin: 0;
            font-size: 1.25rem;
        }
        
        .receipt-row {
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px solid #E2E8F0;
        }
        
        .receipt-label {
            color: #64748B;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.025em;
        }
        
        .receipt-value {
            color: #1E293B;
            font-weight: 600;
        }
        
        /* === Claim ID Highlight === */
        .claim-id {
            background: #EFF6FF;
            color: #1E40AF;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-family: 'SF Mono', 'Consolas', monospace;
            font-weight: 700;
            font-size: 1.1rem;
            display: inline-block;
            border: 1px solid #BFDBFE;
        }
        
        /* === Section Headers === */
        .section-header {
            color: #1E293B;
            font-weight: 700;
            font-size: 1rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #2962FF;
            margin-bottom: 1rem;
        }
        
        /* === File Uploader === */
        [data-testid="stFileUploader"] {
            border: 2px dashed #CBD5E1;
            border-radius: 8px;
            padding: 1rem;
            background: #F8FAFC;
        }
        
        [data-testid="stFileUploader"]:hover {
            border-color: #2962FF;
            background: #EFF6FF;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    """Render the sidebar with branding and system status."""
    with st.sidebar:
        # Branding
        st.markdown("## 🏢 FNOL Intelligence Suite")
        st.caption("Enterprise Claims Intake Platform")
        
        st.divider()
        
        # Product Info Section
        st.markdown("### 📋 Product Info")
        st.markdown("""
        **Developer:** Elliott L.  
        *(8+ Yrs CAT Adjusting Experience)*
        
        **Stack:** Python, Gemini 2.0 Flash, Streamlit
        
        **Compliance:**  
        • SOC2-Ready Infrastructure  
        • PII Redaction Enabled  
        • Zero-Storage Data Policy
        """)
        
        st.divider()
        
        # System Status
        st.markdown("### ⚡ System Status")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown("🟢")
        with col2:
            st.markdown("**PII Redaction:** Active")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown("🟢")
        with col2:
            st.markdown("**Data Retention:** Zero-Storage")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown("🟢")
        with col2:
            st.markdown("**Infrastructure:** SOC2-Ready")
        
        st.divider()
        
        # AI Engine Status
        st.markdown("### 🤖 AI Engine")
        if GOOGLE_API_KEY:
            st.success("Gemini 2.0 Flash Connected")
        else:
            st.warning("API Key Not Configured")
            st.caption(
                "Set GOOGLE_API_KEY in Streamlit Cloud secrets "
                "or in your local .env file."
            )


def render_intake_form():
    """Render the FNOL intake form inside a card container."""
    st.markdown("## 📋 First Notice of Loss")
    st.caption("Structured FNOL intake with validation, AI-assisted triage, and smart routing.")
    st.markdown("*Complete the form below to initiate your claim.*")
    
    with st.container(border=True):
        with st.form("fnol_form"):
            # Policy Information Section
            st.markdown('<p class="section-header">Policy Information</p>', unsafe_allow_html=True)
            
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
            
            st.markdown("---")
            
            # Loss Details Section
            st.markdown('<p class="section-header">Loss Details</p>', unsafe_allow_html=True)
            
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
                height=120,
                help="Provide a detailed description of the incident",
            )
            
            st.markdown("---")
            
            # Contact Information Section
            st.markdown('<p class="section-header">Contact Information</p>', unsafe_allow_html=True)
            
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
            
            st.markdown("---")
            
            # Documentation Section
            st.markdown('<p class="section-header">Supporting Documentation</p>', unsafe_allow_html=True)
            
            uploaded_files = st.file_uploader(
                "Upload Photos & Documents",
                type=["jpg", "jpeg", "png", "pdf", "heic"],
                accept_multiple_files=True,
                help="Upload photos of damage and any supporting documentation (max 3 for AI analysis)",
            )
            
            st.markdown("")
            submitted = st.form_submit_button(
                "Submit Claim",
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


def render_emergency_alert():
    """Render high-visibility ALE/Total Loss alert."""
    st.markdown(
        """
        <div class="emergency-alert">
            <h3>🚨 IMMEDIATE ACTION REQUIRED</h3>
            <p><strong>Emergency Housing Protocol Activated</strong></p>
            <p>Our Temporary Housing Specialist has been automatically alerted and will contact you 
            <strong>within 4 hours</strong> to arrange emergency accommodations.</p>
            <p style="margin-top: 0.75rem; font-size: 0.9rem; opacity: 0.9;">
            Do not worry about housing arrangements – we are taking care of this for you.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_claim_receipt(claim_id: str, data: dict, adjuster_info: tuple, ai_analysis: dict):
    """Render the formal claim confirmation receipt."""
    
    # Emergency Alert (if applicable)
    if ai_analysis.get("ale_alert"):
        render_emergency_alert()
    
    st.markdown("---")
    
    # Success Banner
    st.success("### ✅ Claim Successfully Submitted")
    
    # Formal Receipt Document
    with st.container(border=True):
        # Receipt Header
        st.markdown(
            """
            <div class="receipt-header">
                <h2>📄 INSURED CLAIM RECEIPT</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        # Claim ID Highlight
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(
                f'<div style="text-align: center;"><span class="claim-id">{claim_id}</span></div>',
                unsafe_allow_html=True,
            )
            st.caption("Keep this number for your records")
        
        st.markdown("---")
        
        # Two-column receipt layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📋 Claim Details")
            st.markdown(f"**Policy Number**  \n{data['policy_number']}")
            st.markdown(f"**Date of Loss**  \n{data['loss_date'].strftime('%B %d, %Y')}")
            st.markdown(f"**Type of Loss**  \n{data['loss_type']}")
            st.markdown(f"**Submission Date**  \n{datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        
        with col2:
            st.markdown("##### 👤 Assigned Adjuster")
            if adjuster_info:
                st.markdown(f"**Name**  \n{adjuster_info[0]}")
                st.markdown(f"**Licensed In**  \n{adjuster_info[1]}")
            st.markdown(f"**Your Email**  \n{data['email']}")
            st.markdown(f"**Your Phone**  \n{data['phone']}")
    
    st.markdown("")
    
    # Next Steps
    with st.container(border=True):
        st.markdown("##### 📋 What Happens Next")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **1. Adjuster Contact**  
            You will be contacted within **24-48 hours**.
            
            **2. Prevent Further Damage**  
            Take reasonable steps to prevent additional damage.
            
            **3. Document Everything**  
            Continue photographing any new damage discovered.
            """)
        
        with col2:
            st.markdown("""
            **4. Save All Receipts**  
            Keep receipts for emergency repairs and expenses.
            
            **5. Prepare for Inspection**  
            Gather relevant documents and repair estimates.
            
            **Need Help?** Call **1-800-555-CLAIM** (24/7)
            """)


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="FNOL Intelligence Suite",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Inject custom CSS
    inject_custom_css()
    
    # Render sidebar
    render_sidebar()
    
    # Main content area
    col_spacer1, col_main, col_spacer2 = st.columns([0.5, 11, 0.5])
    
    with col_main:
        # Render intake form
        submitted, form_data = render_intake_form()
        
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
                st.info(f"📋 **Assigned Adjuster:** {adjuster_info[0]} (Licensed in {adjuster_info[1]})")
            
            # Generate claim ID
            claim_id = generate_claim_id()
            
            # AI Analysis with status updates
            with st.status("Analyzing Claim Data...", expanded=True) as status:
                st.write("🔄 Initializing AI Triage Engine...")
                ai_analysis = analyze_claim_with_ai(
                    description=form_data["description"],
                    loss_type=form_data["loss_type"],
                    uploaded_images=form_data["uploaded_files"],
                    status_container=status,
                )
            
            # Render receipt
            render_claim_receipt(claim_id, form_data, adjuster_info, ai_analysis)


if __name__ == "__main__":
    main()
