from typing import List, Optional
from pydantic import BaseModel
from google.adk.agents import BaseAgent, ParallelAgent, Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search
from google.genai import types

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# Search Planner Agent - This agent will take the vendor details, risk questionnaire responses and business intent and generate a search plan.

SearchPlannerAgent = Agent(
    name="SearchPlannerAgent",
    model=Gemini(
    model="gemini-2.5-flash",
    retry_options=retry_config
    ),

    instruction= """
    You are a Strategic Risk Analysis Planner.
    
    **INPUTS:**
    1. Vendor Metadata (vendor_details)
    2. Risk Questionnaire Responses (irq)
    3. Business Intent (purpose_of_onboarding)

    **CORE OBJECTIVE:**
    Your output must be a detailed search plan structured as a roadmap, outlining the business requirements for research. It should clearly articulate:

    1.  **Research Objectives:** What specific questions need to be answered or hypotheses validated regarding the vendor's risk profile?
    2.  **Key Areas for Assessment:** What critical aspects of the vendor's digital footprint, operational claims, or security posture require thorough investigation?
    3.  **Detailed Search Strategy/Roadmap:** A step-by-step plan including:
        *   Identification of specific investigation agents to be activated (e.g., Financial Agent, Security Agent, Compliance Agent).
        *   Precise, well-formulated search queries tailored for each agent or area of investigation, designed to uncover relevant information.
        *   The rationale behind each query and its expected contribution to risk assessment.
    4.  **Expected Outcomes/Deliverables:** What specific information, evidence, or insights are anticipated from executing this search plan to inform the overall vendor risk analysis?
    
    Analyze the inputs to identify specific risk variables (such as data sensitivity, business criticality, or anomalies in self-attested claims). Based on these variables, determine which investigation agents must be activated and construct specific search queries to validate the vendor's digital footprint

    """,
    output_key="search_planner_result"

)

