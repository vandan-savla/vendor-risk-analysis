import streamlit as st
import requests
import json
from datetime import datetime

ADK_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="Vendor Risk Analyzer", layout="wide")

st.title("Vendor Risk Analysis — AI-Powered")


# -------------------------------
# 1. CREATE USER + SESSION
# -------------------------------
if "userId" not in st.session_state:
    st.session_state["userId"] = "u1"

if st.button("Create New Session"):
    resp = requests.post(
        f"{ADK_BASE}/apps/vendor_risk_analysis/users/{st.session_state['userId']}/sessions"
    )
    session = resp.json()
    st.session_state["sessionId"] = session["sessionId"]
    st.success(f"Session created: {session['sessionId']}")

# Require session before moving on
if "sessionId" not in st.session_state:
    st.warning("Click 'Create New Session' first.")
    st.stop()


# -------------------------------
# 2. BUILD ONBOARDING FORM
# -------------------------------
st.header("Vendor Onboarding Form")

vendor_name = st.text_input("Vendor Name")
website_url = st.text_input("Website URL")
service_type = st.text_input("Service Type")
service_description = st.text_area("Service Description")

data_processed = st.multiselect(
    "Data Processed",
    ["PII", "PHI", "PCI", "Analytics Metadata", "Employee Credentials", "Customer Data"]
)

criticality = st.selectbox("Criticality", ["low", "medium", "high"])
certifications = st.multiselect("Certifications", ["SOC 2", "ISO 27001", "GDPR", "HIPAA"])

years = st.number_input("Years in Business", min_value=1)
employees = st.number_input("Employee Count", min_value=1)
region = st.text_input("Region")
self_attested = st.text_area("Self-Attested Incidents")

purpose = st.text_area("Purpose of Onboarding (Business Justification)")

st.subheader("IRQ (Security Questionnaire)")

irq_list = []
irq_count = st.number_input("How many IRQ questions?", min_value=1, max_value=40, value=3)

for i in range(irq_count):
    st.write(f"### IRQ #{i+1}")
    qid = st.text_input(f"IRQ ID #{i+1}", key=f"id_{i}")
    cat = st.text_input(f"Category #{i+1}", key=f"cat_{i}")
    question = st.text_area(f"Question #{i+1}", key=f"q_{i}")
    response = st.text_area(f"Response #{i+1}", key=f"resp_{i}")

    irq_list.append({
        "id": qid,
        "category": cat,
        "question": question,
        "response": response
    })


# -------------------------------
# 3. BUILD JSON PAYLOAD FOR ADK
# -------------------------------
if st.button("Run Analysis"):

    vendor_payload = {
        "vendor_details": {
            "vendor_name": vendor_name,
            "website_url": website_url,
            "service_type": service_type,
            "service_description": service_description,
            "data_processed": data_processed,
            "criticality": criticality,
            "certifications_claimed": certifications,
            "years_in_business": years,
            "employee_count": employees,
            "region": region,
            "self_attested_incidents": self_attested
        },
        "purpose_of_onboarding": purpose,
        "irq": irq_list,
        "report_date": datetime.now().strftime("%Y-%m-%d")
    }

    # MUST be a JSON string inside text
    vendor_payload_str = json.dumps(vendor_payload)

    adk_run_body = {
        "appName": "vendor_risk_analysis",
        "userId": st.session_state["userId"],
        "sessionId": st.session_state["sessionId"],
        "newMessage": {
            "parts": [
                {"text": vendor_payload_str}
            ],
            "role": "user"
        }
    }

    with st.spinner("Running full research pipeline…"):
        resp = requests.post(f"{ADK_BASE}/run", json=adk_run_body)

    if resp.status_code != 200:
        st.error("Error from ADK backend:")
        st.text(resp.text)
        st.stop()

    out = resp.json()

    # Retrieve the final report from ADK state
    state = out.get("state", {})
    report = state.get("risk_reporter_result", "No report generated.")

    st.success("Analysis Complete!")
    st.markdown(report)
