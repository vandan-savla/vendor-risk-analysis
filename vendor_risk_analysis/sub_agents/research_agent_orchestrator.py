from google.adk.agents import Agent, BaseAgent, ParallelAgent
from google.adk.models.google_llm import Gemini
from google.genai import types
from typing import Dict, Any

retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)

# Orchestrator Agent - Based on search planner results, this one decides which agents to invoke and what queries to run.

class OrchestratorAgentOutput(BaseModel):
    breach_agent: bool
    legal_agent: bool
    financial_agent: bool
    compliance_agent: bool
    
    breach_agent_queries: Optional[List[str]]
    legal_agent_queries: Optional[List[str]]
    financial_agent_queries: Optional[List[str]]
    compliance_agent_queries: Optional[List[str]]

OrchestratorAgent = Agent(
    name="OrchestratorAgent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config
    ),
    instruction=""" 
    You are Research Orchestrator Agent which will take the Research plan and generate the List of Agents to be called for research.
    The input will be search_planner_result - {search_planner_result}
    This will be the base to orchestrate the necessary agents further.
    ### 1. AGENT ACTIVATION LOGIC
    Evaluate the input data against the following principles to set the boolean flags:

    * **Breach Agent Logic:** Assess the sensitivity of the data being processed and the vendor's claims regarding their security history. Activate if the potential impact of a data leak is material or if self-reported incident history requires external corroboration.
    * **Legal Agent Logic:** Assess the vendor's exposure to regulatory bodies, potential for intellectual property disputes, or operation within litigious industries. Activate if the vendor's size, region, or industry suggests hidden legal liabilities.
    * **Financial Agent Logic:** Assess the criticality of the vendor to the business continuity and the vendor's implied maturity. Activate if the vendor is a startup, private entity, or if the intended use requires long-term vendor viability.
    * **Compliance Agent Logic:** Assess specific claims made regarding industry standards, certifications, or data sovereignty. Activate to verify the existence and validity of these specific attestations.

    ---

    ### 2. QUERY CONSTRUCTION STRATEGY
    For every activated agent, generate a list of search queries. Do not use templates. Derive the queries directly from the specific details found in the input JSON.

    * **Corroboration:** If the vendor makes a specific positive claim (e.g., specific certifications, specific uptime SLAs), generate queries to find public proof of that claim.
    * **Contradiction:** If the vendor denies a specific negative event (e.g., "No history of breaches"), generate queries designed to uncover evidence that contradicts this denial.
    * **Contextualization:** Combine the Vendor's Name with keywords specific to the *Risk Variables* identified in the analysis. Ensure queries are phrased as search engine inputs (keywords), not conversational questions.
    * **Specificity:** If the input mentions specific technologies, regulations, or regions, include those specific terms in the queries to narrow the search results


    Return List of Agents to run and its queries.
    """,
    output_schema=OrchestratorAgentOutput,
    output_key="orchestrator_agent_result"
)


