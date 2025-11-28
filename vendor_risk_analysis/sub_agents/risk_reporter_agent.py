from typing import List, Optional
from pydantic import BaseModel
from google.adk.agents import BaseAgent, ParallelAgent, Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search
from google.genai import types
from datetime import date
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

RiskReporterAgent= Agent(
    name="RiskReporterAgent",
    model=Gemini(
        model="gemini-2.5-pro",
        retry_options=retry_config
    ),
    instruction="""
        Inputs:
            - input_data = vendor_details, irq
            - All search results 
                1. BreachSearchAgent -> {breach_search_results}
                2. LegalSearchAgent -> {legal_search_results}
                3. FinancialSearchAgent -> {financial_search_results}
                4. ComplianceSearchAgent -> {compliance_search_results}
            - Summary- {summarizer_agent_result}
            - Risk Classification - {risk_classification_result}
            - Report Date - report_date
    
    Combining all this information
    Generate a professional vendor risk report with the following sections
    0. Header - `vendor_name Risk Analysis Report`. 
    1. Sub-Heading - Websit URL, and below that Report Date
    2. Summary and purpose of onboarding and Must have Risk Rating summary. (Simplify)
    3. Sections According to Search Results.
    4. Highlight important figures, key mentions, etc
    5. Detailed Risk rating results along with its reasoning based on Other results
    6. Sources Section where some Only important URLs and other information must be given. 
    7. Conculsion and end of report.
    
    NOTE:
    * All the hyperlinks must be clickable.
    * Make sure to leverage Tables if necessary.
    * The final report must always follow this structure.
    * No Raw HTML tags or any other tags. 
    * Proper Markdown formatting.
    The output must be in Markdown which i can easily convert to pdf.  
    """,
    output_key="risk_reporter_result"
)