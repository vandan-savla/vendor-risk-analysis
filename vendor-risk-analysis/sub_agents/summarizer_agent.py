
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.genai import types


retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)

SummarizerAgent = Agent(
    name="SummarizerAgent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config
    ),
    instruction = """ Take the findings from all the search agents and summarize and highlight key insights.
    1. BreachSearchAgent extractions - {breach_search_results}
    2. LegalSearchAgent extractions - {legal_search_results}
    3. FinancialSearchAgent extractions - {financial_search_results}
    4. ComplianceSearchAgent extractions - {compliance_search_results}
    
    Make the comprehensive Finding report which will be further used for vendor risk analysis.
    This report servers as key reference hence there should not be any mistake.
    """,
    output_key= "summarizer_agent_result"
)