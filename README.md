# FNOL Intelligence Suite

Enterprise-grade First Notice of Loss (FNOL) intake engine for modern Insurtech carriers. Built with Streamlit and powered by Google Gemini 2.0 Flash for intelligent claim triage.

## Features

### 🔐 Security & Compliance
- PII Redaction indicators
- Zero-Storage data retention policy
- SOC2-Ready infrastructure status

### 📋 Intake Form
- Policy Number validation
- Date of Loss with policy period checking
- Type of Loss selection (Fire, Water, Hail, Wind, Theft)
- Detailed loss description
- Contact information capture
- Photo and document upload support

### 🧠 AI Triage Brain (Gemini 2.0 Flash)
- **SIU Risk Scoring**: Identifies red flags like vague timelines, vacancy, and conflicting descriptions
- **Subrogation Detection**: Recognizes potential 3rd party liability (neighbor's tree, manufacturer defect, contractor error)
- **ALE/Total Loss Triage**: Triggers emergency housing alerts for unlivable conditions

### 🚨 Smart Routing
- State-based adjuster assignment (GA, FL, TX, AL)
- Automatic emergency housing protocol activation
- Professional claim receipt generation

## Setup

### Prerequisites
- Python 3.10+
- Google Gemini API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd fnol-intelligence-suite
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### Running the Application

```bash
streamlit run fnol_intelligence_suite.py
```

The application will be available at `http://localhost:8501`

## Configuration

### Policy Period
The default policy effective period is set to January 1, 2026 - December 31, 2026. Modify `POLICY_START_DATE` and `POLICY_END_DATE` in the configuration section to change this.

### State-Adjuster Mapping
Update `STATE_ADJUSTER_MAP` to configure adjuster assignments for different states:

```python
STATE_ADJUSTER_MAP = {
    "GA": "Sarah Mitchell",
    "FL": "Carlos Rodriguez",
    "TX": "Jennifer Thompson",
    "AL": "Michael Chen",
}
```

## License

Proprietary - All rights reserved.
