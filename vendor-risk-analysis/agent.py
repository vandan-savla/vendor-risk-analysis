
from google.adk.agents import SequentialAgent
from google.genai import types
from .sub_agents.research_agents import ParallelResearchTeam
# from .sub_agents.research_agents import LegalSearchAgent, FinancialSearchAgent
from .sub_agents.summarizer_agent import SummarizerAgent
from .sub_agents.risk_classification_agent import RiskClassificationAgent


RootResearchAgent = SequentialAgent(
    name="RootResearchAgent",
    sub_agents = [ParallelResearchTeam ,SummarizerAgent ,RiskClassificationAgent ],
)

root_agent = RootResearchAgent
