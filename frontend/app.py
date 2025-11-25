import streamlit as st
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import os
load_dotenv()

ADK_BASE = os.getenv("ADK_BASE")

st.set_page_config(page_title="Vendor Risk Analyzer", layout="wide")

st.title("Vendor Risk Analysis - AI-Powered")

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
    print(session)
    st.session_state["sessionId"] = session["id"]
    st.success(f"Session created: {session['id']}")

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

st.subheader("Data Processed by Vendor")

common_data_types = [
    "PII (Personal Data)",
    "PHI (Health Data)",
    "PCI (Payment Card Data)",
    "Authentication Data",
    "Analytics Metadata",
    "Employee Credentials",
    "Customer Data",
    "Device Telemetry",
    "Cloud Logs",
    "Source Code",
]

selected_common = st.multiselect(
    "Select Common Data Types (optional)",
    common_data_types
)

custom_data = st.text_area(
    "Add Custom Data Types (comma-separated)",
    placeholder="Example: Financial reports, Uploaded PDFs, GPS location data"
)

# merge into a single list
data_processed = selected_common.copy()

if custom_data.strip():
    custom_items = [x.strip() for x in custom_data.split(",") if x.strip()]
    data_processed.extend(custom_items)


criticality = st.selectbox("Criticality", ["low", "medium", "high"])
certifications = st.multiselect("Certifications", ["SOC 2", "ISO 27001", "GDPR", "HIPAA"])

years = st.number_input("Years in Business", min_value=1)
employees = st.number_input("Employee Count", min_value=1)
region = st.text_input("Region")
self_attested = st.text_area("Self-Attested Incidents")

purpose = st.text_area("Purpose of Onboarding (Business Justification)")

st.subheader("IRQ (Security Questionnaire)")
# -------------------------------
# IRQ MASTER QUESTIONNAIRE (20 QUESTIONS)
# -------------------------------

irq_master = [
    ("GEN-01", "General", "Describe the services provided and how customer data will be used."),
    ("GEN-02", "General", "List all categories of data you expect to process (PII, PHI, PCI, etc.)."),
    ("SEC-01", "Information Security", "Do you have valid third-party security certifications? Provide scope and audit date."),
    ("SEC-02", "Information Security", "Do you have a dedicated security team and a formal information security policy?"),
    ("SEC-03", "Information Security", "Describe your vulnerability management and patching process."),
    ("ACC-01", "Access Control", "Do you enforce Multi-Factor Authentication (MFA) for internal and administrative access?"),
    ("ACC-02", "Access Control", "How do you manage provisioning and de-provisioning of employee access?"),
    ("ACC-03", "Access Control", "Do you support SSO/SAML for customer login?"),
    ("DAT-01", "Data Protection", "Describe how data is encrypted in transit."),
    ("DAT-02", "Data Protection", "Describe how data is encrypted at rest."),
    ("DAT-03", "Data Protection", "What is your customer data retention and deletion policy?"),
    ("DAT-04", "Data Protection", "Where is customer data geographically stored? Provide regions."),
    ("TPRM-01", "Third-Party Management", "List your critical sub-processors and their roles."),
    ("TPRM-02", "Third-Party Management", "Do you perform annual security reviews of your sub-processors?"),
    ("INC-01", "Incident Response", "Do you have a formal Incident Response Plan (IRP)?"),
    ("INC-02", "Incident Response", "How quickly do you notify customers after confirming a breach?"),
    ("BCP-01", "Business Continuity", "Describe your backup strategy and frequency."),
    ("BCP-02", "Business Continuity", "What are your RTO and RPO objectives?"),
    ("APP-01", "Application Security", "Do you conduct annual penetration testing? Provide details."),
    ("APP-02", "Application Security", "Do you use SAST/DAST or CI/CD security scanning tools?")
]

irq_list = []

for qid, category, question in irq_master:
    st.write(f"#### {qid} - {category}")
    st.write(f"##### {question}")
    response = st.text_area(f"Response: {qid}", key=qid)
    irq_list.append({
        "id": qid,
        "category": category,
        "question": question,
        "response": response
    })




# -------------------------------
# 3. BUILD JSON PAYLOAD FOR ADK
# -------------------------------
if st.button("Run Analysis"):
    # For testing purpose
    
    # vendor_payload = {
    #     "vendor_details": {
    #         "vendor_name": "LucidSuite Analytics",
    #         "website_url": "https://www.lucidsuite.io",
    #         "service_type": "Cloud SaaS / Workflow Analytics",
    #         "service_description": "LucidSuite provides a cloud-based platform that helps our internal teams visualize process bottlenecks, track workflow performance, and generate operational insights. The platform runs as a standard SaaS in their managed cloud environment.",
    #         "data_processed": [
    #         "PII (employee names & email IDs for login)",
    #         "Analytics Metadata",
    #         "Workflow behavioral data",
    #         "Uploaded CSVs (non-sensitive)"
    #         ],
    #         "criticality": "medium",
    #         "certifications_claimed": [
    #         "SOC 2 Type II",
    #         "ISO 27001"
    #         ],
    #         "years_in_business": 7,
    #         "employee_count": 180,
    #         "region": "US / Canada",
    #         "self_attested_incidents": "No known outages or security incidents affecting customer data in the last 24 months."
    #     },
    #     "purpose_of_onboarding": "We are onboarding LucidSuite Analytics to provide workflow visibility dashboards for our internal Operations and Product teams. The tool will help streamline our process analysis activities and reduce manual reporting efforts. This onboarding is part of our initiative to centralize operational analytics for internal optimization. No customer PII, PHI, or PCI data will be uploaded into the vendor’s environment; only internal employee identifiers and aggregated workflow metadata will be processed.",
    #     "irq": [
    #         {
    #         "id": "GEN-01",
    #         "category": "General",
    #         "question": "Describe the services provided and how customer data will be used.",
    #         "response": "LucidSuite will ingest internal employee identifiers and workflow metadata to generate analytics dashboards. No highly sensitive data is involved. They use our data only for delivering the analytics service."
    #         },
    #         {
    #         "id": "GEN-02",
    #         "category": "General",
    #         "question": "List all categories of data you expect to process (PII, PHI, PCI, etc.).",
    #         "response": "Employee PII (email, name), basic metadata from workflow interactions, and uploaded CSV data containing operational stats. No PHI, PCI, or customer data."
    #         },
    #         {
    #         "id": "SEC-01",
    #         "category": "Information Security",
    #         "question": "Do you have valid third-party security certifications? Provide scope and audit date.",
    #         "response": "Vendor claims SOC 2 Type II and ISO 27001 certifications as of Q2 2024 covering cloud infrastructure, data handling, and operational controls."
    #         },
    #         {
    #         "id": "SEC-02",
    #         "category": "Information Security",
    #         "question": "Do you have a dedicated security team and a formal information security policy?",
    #         "response": "Yes, the vendor has a dedicated security function with a CISO and publishes their information security policy on their trust center."
    #         },
    #         {
    #         "id": "SEC-03",
    #         "category": "Information Security",
    #         "question": "Describe your vulnerability management and patching process.",
    #         "response": "Vendor follows a 30-day SLA for non-critical patches and 48-hour patching for critical CVEs. They use automated scanning tools."
    #         },
    #         {
    #         "id": "ACC-01",
    #         "category": "Access Control",
    #         "question": "Do you enforce Multi-Factor Authentication (MFA) for internal and administrative access?",
    #         "response": "Yes, MFA is mandatory for all internal admin access. SSO available for customers."
    #         },
    #         {
    #         "id": "ACC-02",
    #         "category": "Access Control",
    #         "question": "How do you manage provisioning and de-provisioning of employee access?",
    #         "response": "Access is automated via HR events. De-provisioning is completed within 12 hours of employee exit."
    #         },
    #         {
    #         "id": "ACC-03",
    #         "category": "Access Control",
    #         "question": "Do you support SSO/SAML for customer login?",
    #         "response": "Yes, SSO using Okta and Azure AD."
    #         },
    #         {
    #         "id": "DAT-01",
    #         "category": "Data Protection",
    #         "question": "Describe how data is encrypted in transit.",
    #         "response": "TLS 1.2+ enforced across all endpoints with HSTS."
    #         },
    #         {
    #         "id": "DAT-02",
    #         "category": "Data Protection",
    #         "question": "Describe how data is encrypted at rest.",
    #         "response": "AES-256 at rest on their cloud storage and database systems."
    #         },
    #         {
    #         "id": "DAT-03",
    #         "category": "Data Protection",
    #         "question": "What is your customer data retention and deletion policy?",
    #         "response": "Data is retained for 30 days post-termination unless otherwise required and removed from backups within 90 days."
    #         },
    #         {
    #         "id": "DAT-04",
    #         "category": "Data Protection",
    #         "question": "Where is customer data geographically stored?",
    #         "response": "US-based cloud regions with redundancy across East and Central."
    #         },
    #         {
    #         "id": "TPRM-01",
    #         "category": "Third-Party Management",
    #         "question": "List your critical sub-processors and their roles.",
    #         "response": "AWS for hosting, Snowflake for analytics backend."
    #         },
    #         {
    #         "id": "TPRM-02",
    #         "category": "Third-Party Management",
    #         "question": "Do you perform annual security reviews of your sub-processors?",
    #         "response": "Vendor states they perform annual checks but haven’t provided a detailed list yet."
    #         },
    #         {
    #         "id": "INC-01",
    #         "category": "Incident Response",
    #         "question": "Do you have a formal Incident Response Plan (IRP)?",
    #         "response": "They have an IRP aligned with SOC 2 controls."
    #         },
    #         {
    #         "id": "INC-02",
    #         "category": "Incident Response",
    #         "question": "How quickly do you notify customers after confirming a breach?",
    #         "response": "Vendor claims 48-hour breach notification window."
    #         },
    #         {
    #         "id": "BCP-01",
    #         "category": "Business Continuity",
    #         "question": "Describe your backup strategy and frequency.",
    #         "response": "Daily backups with multi-region replication."
    #         },
    #         {
    #         "id": "BCP-02",
    #         "category": "Business Continuity",
    #         "question": "What are your RTO and RPO objectives?",
    #         "response": "RTO of 12 hours, RPO of 4 hours."
    #         },
    #         {
    #         "id": "APP-01",
    #         "category": "Application Security",
    #         "question": "Do you conduct annual penetration testing?",
    #         "response": "Yes, performed by a third-party vendor yearly."
    #         },
    #         {
    #         "id": "APP-02",
    #         "category": "Application Security",
    #         "question": "Do you use SAST/DAST or CI/CD security scanning tools?",
    #         "response": "They use CI-integrated static and dependency scanners."
    #         }
    #     ],
    #     "report_date": "2025-11-24"
    #     }


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
    print(out)
    # Retrieve the final report from ADK state
    # state = out.get("state", {})
    # report = state.get("risk_reporter_result", "No report generated.")
    last_event = out[-1]

# Safely extract final report
    report = (
        last_event
        .get("actions", {})
        .get("stateDelta", {})
        .get("risk_reporter_result", "No final report generated.")
    )
    st.markdown(report)
