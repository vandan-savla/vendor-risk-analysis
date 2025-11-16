from google.adk.agents import Agent, ParallelAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search
from google.genai import types

retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)


BreachSearchAgent = Agent(
    name="BreachSearchAgent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config
    ),
    instruction="""
    You are a cybersecurity breach researcher.

    Input available: vendor_name  
    Your task: Identify ANY public breach-related signals connected to the vendor.


    =====================
    ### WHAT TO SEARCH FOR
    - Confirmed data breaches
    - Ransomware incidents
    - Past hacking incidents
    - Vulnerability disclosures
    - Mentions in:
    - News sites
    - Cybersecurity blogs
    - Reddit cybersecurity threads
    - Hacker forums (via search index only)
    - CVE listings for vendor products
    - Government breach disclosure portals

    =====================
    ### OUTPUT REQUIREMENTS
    Return a structured summary containing:
    - Any identified breaches
    - Severity indicators (low/medium/high)
    - Dates (if available)
    - Source URLs
    - Whether incidents were resolved or ongoing

""",
    tools=[google_search],
    output_key="breach_search_results"
)


LegalSearchAgent = Agent(
    name="LegalSearchAgent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config
    ),
    instruction="""
        You are a legal risk researcher.

        Input available: vendor_name  
        Your task: Identify ANY public legal or regulatory risks linked to the vendor.

        =====================
        ### WHAT TO SEARCH FOR
        - Ongoing or past lawsuits
        - Class-action litigation
        - Regulatory fines (GDPR, FTC, CCI, SEC, etc.)
        - Consumer protection violations
        - Court filings
        - Legal disputes involving:
        - parent company
        - subsidiaries
        - sister companies (same corporate group)

        =====================
        ### OUTPUT REQUIREMENTS
        Return structured information:
        - Issue type
        - Date (if available)
        - Court / regulator involved
        - Severity (low/medium/high)
        - URLs referencing evidence

        If nothing found - state "No public legal signals detected."
    """,
    tools=[google_search],
    output_key="legal_search_results"
)


FinancialSearchAgent = Agent(
    name="FinancialSearchAgent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config
    ),
    instruction="""
        You are a financial risk analyst.

        Input available: vendor_name  
        Your task: Identify ANY indicators of financial risk.

        =====================
        ### WHAT TO SEARCH FOR
        - Layoffs (trend, frequency)
        - Bankruptcy filings
        - Fraud allegations
        - Revenue decline or instability
        - Funding issues
        - VC negative commentary
        - Poor financial performance indicators
        - Customer complaints about:
        - billing practices
        - sudden service outages (implying cost cuts)
        - Investor or analyst reports

        =====================
        ### OUTPUT REQUIREMENTS
        Return structured summary:
        - Category (layoffs, fraud, bankruptcy, etc.)
        - Severity (low/medium/high)
        - Evidence URLs
        - Timeframe (recent/past)
        - Market sentiment if visible

        If no meaningful findings - state "No public financial warning signs found."
    """,
    tools=[google_search],
    output_key="financial_search_results"
)



ComplianceSearchAgent = Agent(
    name= "ComplianceSearchAgent",
    model=Gemini(   
        model="gemini-2.5-flash",
        retry_options=retry_config
    ),
    instruction=""" 
        You are a compliance posture evaluator.

        Input available: vendor_name and website_url
        Your task: Determine whether the vendor appears compliant with relevant industry standards.

        =====================
        ### WHAT TO ANALYZE
        - Does vendor publicly claim certifications?
        - Are certifications **verifiable**?
        - Does vendor maintain a trust center?
        - Does privacy policy mention frameworks?
        - If a vendor operates in a regulated domain:
        - Healthcare - HIPAA
        - Payments/Fintech - PCI DSS
        - SaaS - SOC2, ISO 27001
        - EU data handling - GDPR
        - Look for:
        - mismatched or fake claims  
        - expired certificates  
        - unverifiable claims  
        - third-party audit references

        =====================
        ### OUTPUT REQUIREMENTS
        Return structured summary:
        - Claimed certifications
        - Evidence URLs
        - Whether claims appear credible
        - Missing certification red flags
        - Severity of compliance gap (low/medium/high)

        If unclear - state "Insufficient public evidence to confirm compliance."
    
     """,
    tools=[google_search],
    output_key="compliance_search_results",
)


ParallelResearchTeam = ParallelAgent(
    name="ParallelResearchTeam",
    sub_agents=[BreachSearchAgent,LegalSearchAgent,FinancialSearchAgent, ComplianceSearchAgent],
)
