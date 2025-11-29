from pydantic import BaseModel
from typing import List, Literal


class RiskClassificationOutput(BaseModel):
    # Define fields to only accept 'low', 'medium', or 'high'
    security_risk: Literal['low', 'medium', 'high']
    legal_risk: Literal['low', 'medium', 'high']
    financial_risk: Literal['low', 'medium', 'high']
    reputation_risk: Literal['low', 'medium', 'high']
    compliance_risk: Literal['low', 'medium', 'high']
    overall_risk_rating: Literal['low', 'medium', 'high']
    
    reasoning_summary: str

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.genai import types

retry_config = types.HttpRetryOptions(attempts=5, exp_base=7, initial_delay=1, http_status_codes=[429,500,503,504])

RiskClassificationAgent = Agent(
    name="RiskClassificationAgent",
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    instruction="""
        You are an expert Third-Party Risk Analyst.

        Inputs:
        - summarizer_agent_result (structured summarizer output)
        - vendor_details (onboarding form) with purpose_of_onboarding and data_processed

        Behavior:
        - For each category (security/legal/financial/reputation/compliance):
        * Consider only findings marked as relevant (high/medium) by Summarizer.
        * For historical findings older than 3 years and marked 'resolved' -> treat as low.
        * For findings unrelated to purpose_of_onboarding -> treat as low.
        * Use the following labels: low, medium, high (lowercase).
        - Compute overall_risk_rating:
        - high if any category is high AND that high must be relevant to purpose_of_onboarding
        - medium if 2+ categories are medium or one high but with mitigating evidence
        - low otherwise

        Be concise in reasoning_summary and reference the most important evidence lines.
    """,
    output_schema=RiskClassificationOutput,
    output_key="risk_classification_result"
)
