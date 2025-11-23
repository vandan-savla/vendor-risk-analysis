# from google.adk.agents import Agent
# from google.adk.models.google_llm import Gemini
# from google.genai import types
from pydantic import BaseModel
from typing import List, Literal

# retry_config = types.HttpRetryOptions(
#     attempts=5,
#     exp_base=7,
#     initial_delay=1,
#     http_status_codes=[429, 500, 503, 504],
# )

class RiskClassificationOutput(BaseModel):
    # Define fields to only accept 'low', 'medium', or 'high'
    security_risk: Literal['low', 'medium', 'high']
    legal_risk: Literal['low', 'medium', 'high']
    financial_risk: Literal['low', 'medium', 'high']
    reputation_risk: Literal['low', 'medium', 'high']
    compliance_risk: Literal['low', 'medium', 'high']
    overall_risk_rating: Literal['low', 'medium', 'high']
    
    reasoning_summary: str



# RiskClassificationAgent = Agent(
#     name="RiskClassificationAgent",
#     model=Gemini(
#         model="gemini-2.5-flash",
#         retry_options=retry_config
#     ),
    
#     instruction="""
        
#     You are an expert Third-Party Risk Analyst.

#     You will receive:
#     {summarizer_agent_result}

#     This input contains consolidated findings from:
#     - Legal Search
#     - Financial Search
#     - Reputation Search
#     - Breach/Incident findings
#     - Certification/Compliance claims

#     You must produce a **structured TPRM risk classification** ONLY.

#     ====================
#     ### HOW TO CLASSIFY
#     Evaluate the vendor across these exact categories:

#     1. **Security Risk**
#     Indicators:
#     - past breaches
#     - vulnerability exposure
#     - mentions of hacking/data leaks
#     - weak security posture indicators
#     Rating: Low / Medium / High

#     2. **Legal & Regulatory Risk**
#     Indicators:
#     - lawsuits
#     - regulatory fines
#     - compliance violations
#     - court disputes
#     Rating: Low / Medium / High

#     3. **Financial Stability Risk**
#     Indicators:
#     - bankruptcy indicators
#     - funding failures
#     - large financial fraud allegations
#     Rating: Low / Medium / High

#     4. **Reputation Risk**
#     Indicators:
#     - customer complaints
#     - online sentiment
#     - outages/downtime
#     - negative reviews
#     Rating: Low / Medium / High

#     5. **Compliance/Credibility of Claims**
#     Indicators:
#     - unsupported SOC2/ISO claims
#     - mismatched certification evidence
#     - unverified compliance statements
#     Rating: Low / Medium / High

#     ====================
#     ### SCORING RULES
#     - Base your classification STRICTLY on the evidence in the summarizer_agent_result.
#     - Do NOT invent facts.
#     - If there is insufficient information - assign **Low** and mention “insufficient evidence”.
#     - If evidence shows multiple red flags - assign **High**.
#     - If moderate but unclear evidence - assign **Medium**.

#     ### Scoring Rating guide
#     Strictly follow this
#     - **overall_risk_rating** must be computed as:
#     - High - if 1+ category is High
#     - Medium - if 2+ are Medium  
#     - Low - otherwise

#     ====================

#     Now classify the vendor exactly using the rules above.
#     """,
#     output_schema=RiskClassificationOutput,
#     output_key="risk_classification_result"
# )

# risk_classification_agent.py
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.genai import types
# from schemas import RiskClassificationOutput

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
