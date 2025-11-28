import streamlit as st
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import os
load_dotenv()

ADK_BASE_URL = os.getenv("ADK_BASE_URL")

st.set_page_config(page_title="VendorScan", layout="wide")

st.title("VendorScan - AI powered vendor risk analyst")

# -------------------------------
# 1. CREATE USER + SESSION
# -------------------------------
if "userId" not in st.session_state:
    st.session_state["userId"] = "u1"

if st.button("Create New Session"):
    resp = requests.post(
        f"{ADK_BASE_URL}/apps/vendor_risk_analysis/users/{st.session_state['userId']}/sessions"
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
certifications = st.multiselect("Certifications", ["SOC 2 Type I", "SOC 2 Type II" , "ISO/IEC 27001", "GDPR", "HIPAA", "PCI DSS", "CCPA", "SOX (Sarbanes-Oxley Act)"])

years = st.number_input("Years in Business", min_value=1)
employees = st.number_input("Employee Count", min_value=1)
region = st.text_input("Region")
self_attested = st.text_area("Self-Attested Incidents")

purpose = st.text_area("Purpose of Onboarding (Business Justification)")

st.subheader("Inherent Risk Questionnaire (Self - Assessment)")
# -------------------------------
# IRQ MASTER QUESTIONNAIRE (20 QUESTIONS)
# -------------------------------

irq_master = [
    ("GEN-01", "General", 
     "What services are you expecting this vendor to provide, and how will our organization use those services?"),
    
    ("GEN-02", "General", 
     "What types of data from our side will the vendor need to process or access (e.g., PII, PHI, PCI, logs, analytics data)?"),
    
    ("SEC-01", "Information Security", 
     "Based on your review of the vendor’s website or documentation, what security certifications do they publicly claim (e.g., SOC 2, ISO 27001)?"),
    
    ("SEC-02", "Information Security", 
     "Does the vendor appear to have a dedicated security function or team based on publicly available information?"),
    
    ("SEC-03", "Information Security", 
     "Does the vendor indicate how they handle security updates, vulnerability management, or patching in their platform or documentation?"),
    
    ("ACC-01", "Access Control", 
     "What authentication requirements does the vendor support (e.g., MFA, SSO, SAML)? Based on your understanding, will our users authenticate securely?"),
    
    ("ACC-02", "Access Control", 
     "To your knowledge, how does the vendor handle employee access on their side (provisioning/de-provisioning)? If documented, note it here."),
    
    ("ACC-03", "Access Control", 
     "Will our employees access the vendor via Single Sign-On (SSO)? If yes, what method is supported?"),
    
    ("DAT-01", "Data Protection", 
     "Does the vendor disclose how data is encrypted when transmitted? If yes, describe what is mentioned (e.g., TLS 1.2+)."),
    
    ("DAT-02", "Data Protection", 
     "Does the vendor disclose whether customer data is encrypted at rest? If yes, provide details."),
    
    ("DAT-03", "Data Protection", 
     "What is the vendor’s stated data retention or deletion policy for customer data after contract termination?"),
    
    ("DAT-04", "Data Protection", 
     "Where does the vendor store customer data geographically (US, EU, multi-region) based on their documentation?"),
    
    ("TPRM-01", "Third-Party Management", 
     "List any sub-processors the vendor uses that you are aware of (e.g., AWS, GCP, email providers)."),
    
    ("TPRM-02", "Third-Party Management", 
     "Does the vendor state whether they perform periodic reviews or assessments of their own sub-processors?"),
    
    ("INC-01", "Incident Response", 
     "Does the vendor publicly document an Incident Response Plan or security incident process? If yes, summarize."),
    
    ("INC-02", "Incident Response", 
     "What is the stated vendor notification timeline if an incident affects our data (e.g., 24h, 48h, 72h)?"),
    
    ("BCP-01", "Business Continuity", 
     "Does the vendor disclose their backup frequency or disaster recovery approach on their website or trust center?"),
    
    ("BCP-02", "Business Continuity", 
     "If available, what are the published RTO (Recovery Time Objective) and RPO (Recovery Point Objective) values?"),
    
    ("APP-01", "Application Security", 
     "Does the vendor publish information about conducting penetration testing or running a bug bounty program?"),
    
    ("APP-02", "Application Security", 
     "Does the vendor indicate using security scanning tools (SAST, DAST, SCA) within their development lifecycle?")
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
    # "vendor_details": {
    #     "vendor_name": "LucidSuite Analytics",
    #     "website_url": "https://www.lucidsuite.io",
    #     "service_type": "Cloud SaaS / Workflow Analytics",
    #     "service_description": "LucidSuite provides a workflow visualization and operational analytics SaaS used by our internal Operations and Product teams to track process health, identify bottlenecks, and generate performance dashboards.",
    #     "data_processed": [
    #     "Basic employee PII for login (names, emails)",
    #     "Workflow interaction metadata",
    #     "Uploaded CSV files with internal process metrics",
    #     "Analytics Metadata"
    #     ],
    #     "criticality": "medium",
    #     "certifications_claimed": [
    #     "SOC 2 Type II",
    #     "ISO 27001"
    #     ],
    #     "years_in_business": 7,
    #     "employee_count": 180,
    #     "region": "US / Canada",
    #     "self_attested_incidents": "Based on publicly available information, there have been no notable security incidents or outages impacting customer data in the past two years."
    # },
    # "purpose_of_onboarding": "We are onboarding LucidSuite Analytics to support internal workflow optimization efforts. The platform will allow our teams to visualize operational trends and improve reporting efficiency. Only internal employee identifiers and workflow metadata will be processed—no PHI, PCI, or customer PII is uploaded to the vendor environment.",
    # "irq": [
    #     {
    #     "id": "GEN-01",
    #     "category": "General",
    #     "question": "What services are you expecting this vendor to provide, and how will our organization use those services?",
    #     "response": "LucidSuite will be used to visualize internal process metrics and generate operational dashboards. It supports non-customer-facing analytics and helps internal teams monitor workflow performance."
    #     },
    #     {
    #     "id": "GEN-02",
    #     "category": "General",
    #     "question": "What types of data from our side will the vendor need to process or access (e.g., PII, PHI, PCI, logs, analytics data)?",
    #     "response": "Only basic employee PII for login (name, email), workflow metadata, and optional CSV uploads with operational metrics."
    #     },
    #     {
    #     "id": "SEC-01",
    #     "category": "Information Security",
    #     "question": "Based on your review of the vendor’s website or documentation, what security certifications do they publicly claim (e.g., SOC 2, ISO 27001)?",
    #     "response": "Their trust center lists SOC 2 Type II and ISO 27001, both current as of mid-2024."
    #     },
    #     {
    #     "id": "SEC-02",
    #     "category": "Information Security",
    #     "question": "Does the vendor appear to have a dedicated security function or team based on publicly available information?",
    #     "response": "Yes. They reference a CISO-led security team and publish several security policies on their trust center."
    #     },
    #     {
    #     "id": "SEC-03",
    #     "category": "Information Security",
    #     "question": "Does the vendor indicate how they handle security updates, vulnerability management, or patching in their platform or documentation?",
    #     "response": "They state that critical patches are applied within 48 hours and general patches within 30 days, supported by automated scanning tools."
    #     },
    #     {
    #     "id": "ACC-01",
    #     "category": "Access Control",
    #     "question": "What authentication requirements does the vendor support (e.g., MFA, SSO, SAML)?",
    #     "response": "MFA is enforced for their internal staff. They support customer SSO using Okta or Azure AD."
    #     },
    #     {
    #     "id": "ACC-02",
    #     "category": "Access Control",
    #     "question": "To your knowledge, how does the vendor handle employee access on their side (provisioning/de-provisioning)?",
    #     "response": "Their documentation indicates automated HR-driven provisioning and same-day de-provisioning for departures."
    #     },
    #     {
    #     "id": "ACC-03",
    #     "category": "Access Control",
    #     "question": "Will our employees access the vendor via Single Sign-On (SSO)?",
    #     "response": "Yes, we plan to integrate via SSO using our Okta tenant."
    #     },
    #     {
    #     "id": "DAT-01",
    #     "category": "Data Protection",
    #     "question": "Does the vendor disclose how data is encrypted when transmitted?",
    #     "response": "TLS 1.2+ with HSTS enabled across endpoints."
    #     },
    #     {
    #     "id": "DAT-02",
    #     "category": "Data Protection",
    #     "question": "Does the vendor disclose whether customer data is encrypted at rest?",
    #     "response": "Yes. All stored data is encrypted with AES-256 according to their security documentation."
    #     },
    #     {
    #     "id": "DAT-03",
    #     "category": "Data Protection",
    #     "question": "What is the vendor’s stated data retention or deletion policy for customer data after contract termination?",
    #     "response": "They delete active data within 30 days after account closure and purge backups within 90 days."
    #     },
    #     {
    #     "id": "DAT-04",
    #     "category": "Data Protection",
    #     "question": "Where does the vendor store customer data geographically (US, EU, multi-region) based on their documentation?",
    #     "response": "They use US-based cloud regions with redundancy across multiple availability zones."
    #     },
    #     {
    #     "id": "TPRM-01",
    #     "category": "Third-Party Management",
    #     "question": "List any sub-processors the vendor uses that you are aware of.",
    #     "response": "AWS for primary hosting and Snowflake for analytics backend, based on their published sub-processor list."
    #     },
    #     {
    #     "id": "TPRM-02",
    #     "category": "Third-Party Management",
    #     "question": "Does the vendor state whether they perform periodic reviews or assessments of their own sub-processors?",
    #     "response": "They mention performing annual reviews, though the documentation does not provide deep detail."
    #     },
    #     {
    #     "id": "INC-01",
    #     "category": "Incident Response",
    #     "question": "Does the vendor publicly document an Incident Response Plan or security incident process?",
    #     "response": "Yes, the IRP is referenced on their trust center and aligns to SOC 2 requirements."
    #     },
    #     {
    #     "id": "INC-02",
    #     "category": "Incident Response",
    #     "question": "What is the vendor's stated notification timeline if an incident affects our data?",
    #     "response": "Their documentation states a 48-hour customer notification window."
    #     },
    #     {
    #     "id": "BCP-01",
    #     "category": "Business Continuity",
    #     "question": "Does the vendor disclose their backup frequency or disaster recovery approach on their website or trust center?",
    #     "response": "Yes, daily backups replicated across multiple regions."
    #     },
    #     {
    #     "id": "BCP-02",
    #     "category": "Business Continuity",
    #     "question": "If available, what are the published RTO (Recovery Time Objective) and RPO (Recovery Point Objective) values?",
    #     "response": "RTO is listed as 12 hours; RPO is 4 hours."
    #     },
    #     {
    #     "id": "APP-01",
    #     "category": "Application Security",
    #     "question": "Does the vendor publish information about conducting penetration testing or running a bug bounty program?",
    #     "response": "They state that an external firm performs annual penetration testing."
    #     },
    #     {
    #     "id": "APP-02",
    #     "category": "Application Security",
    #     "question": "Does the vendor indicate using security scanning tools (SAST, DAST, SCA)?",
    #     "response": "Yes, their SDLC documentation mentions static code scanning and dependency scanning."
    #     }
    # ],
    # "report_date": "2025-11-28"
    # }


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
        resp = requests.post(f"{ADK_BASE_URL}/run", json=adk_run_body)

    if resp.status_code != 200:
        st.error("Error from ADK backend:")
        st.text(resp.text)
        st.stop()

    out = resp.json()
    # print(out)
    
    last_event = out[-1]

# Safely extract final report
    report = (
        last_event
        .get("actions", {})
        .get("stateDelta", {})
        .get("risk_reporter_result", "No final report generated.")
    )
    st.markdown(report)
