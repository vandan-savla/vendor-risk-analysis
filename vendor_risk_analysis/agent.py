
from google.adk.agents import SequentialAgent
from .sub_agents.research_agents import ParallelResearchTeam, BreachSearchAgent, LegalSearchAgent, FinancialSearchAgent, ComplianceSearchAgent 
from .sub_agents.summarizer_agent import SummarizerAgent
from .sub_agents.risk_classification_agent import RiskClassificationAgent
from .sub_agents.search_planner_agent import SearchPlannerAgent
from .sub_agents.research_agent_orchestrator import OrchestratorAgent
from .sub_agents.risk_reporter_agent import RiskReporterAgent

sub_agents_map = {
    "breach": BreachSearchAgent,
    "legal": LegalSearchAgent,
    "financial": FinancialSearchAgent,
    "compliance": ComplianceSearchAgent
}

RootResearchAgent = SequentialAgent(
    name="RootResearchAgent",
    sub_agents = [SearchPlannerAgent, OrchestratorAgent , ParallelResearchTeam, SummarizerAgent ,RiskClassificationAgent,RiskReporterAgent],
)

root_agent = RootResearchAgent
