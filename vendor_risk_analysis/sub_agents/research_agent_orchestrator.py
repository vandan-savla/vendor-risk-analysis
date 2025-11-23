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

OrchestratorAgent = Agent(
    name="OrchestratorAgent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config
    ),
    instruction=""" 
    You are Research Orchestrator Agent which will take the Research plan and generate the List of Agents to be called for research in parallel mode.
    The input will be search_planner_result - {search_planner_result}
    This will be the base to orchestrate the necessary agents further.
    
    Return List of Agents to run and its queries.
    """,
    # output_schema=OrchestratorAgentOutput,
    output_key="orchestrator_agent_result"
)


