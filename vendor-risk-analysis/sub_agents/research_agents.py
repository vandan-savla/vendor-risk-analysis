from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import AgentTool, FunctionTool, google_search
from google.genai import types
from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import AgentTool, FunctionTool, google_search
from google.genai import types


retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)


BreachSearchAgent = Agent(
    name = "BreachSearchAgent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config
    ),   
    instruction=""" 
    Given vendor_name Research based on the following rules:
    Are there any frequent data breaches happend which has impacted the organization.
    Do they resolve and mitigate cyberattacks regularly
    Do they happen to give employees training regarding cyber attacks?
    Find comprehensive details about the vendor's cyber posture.
    
    Take consideration the following paths
    
    News articles
    Cybersecurity blogs
    Reddit threads
    Hacker forums (scrapable indirectly via Google Search)
    CVE listings for vendor products
    Government breach notification lists
    
    """,
    tools=[google_search],
    output_key="breach_search_results",
)



LegalSearchAgent = Agent(
    name="LegalSearchAgent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config
    ),
    instruction = """ Based on the given vendor - vendor_name
    Research based on the following rules:
    1. If the vendor is currently been facing legal issues.
    2. Is this vendor been penalized for breaching any major law.
    3. How many lawsuits has been going on till date.
    4. Its sister companies also facing same issues ?
    and many more 
    
    Take consideration the following paths
    
    News reports

    Press releases

    Public court portals

    Court reporting websites

    Wikipedia entries

    Consumer complaint forums
    
    Extract comprehensive details using google_search tool
    
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
    instruction = """ Based on the given vendor - vendor_name
    Research based on the following rules:
    1. What is the financial posture of the vendor ?
    2. Is there been any financial fraud happend ? 
    3. Are there frequent layoffs happens by that vendor?
    4. Does vendor has filed bankruptcy?
    5. Are any negative reviews by VCs or any funding issues
    6. Negative customer reviews.

    Also general findings based on finance,    can use Yahoo finance website for balance sheets, and other financial metrics,
    forums, for sentiment findings and legal websites for fraud and other findings.
    
    Extract comprehensive details using google_search tool
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
    Search if vendor is compliant on various domains 
    examples SOC2, ISO, PCI DSS, HIPPA, etc
    whatever the vendor's domain is check for its compliance status. 
    If it is not compliant raise it as red flag.
    You need to check privacy policy from its website and trust centers.
    Generate comphrensive result highlighting important points.
    """,
    tools=[google_search],
    output_key="compliance_search_results",
)


ParallelResearchTeam = ParallelAgent(
    name="ParallelResearchTeam",
    sub_agents=[BreachSearchAgent,LegalSearchAgent,FinancialSearchAgent, ComplianceSearchAgent],
)

# ResearchLoopAgent = LoopAgent(
#     name="ResearchLoopAgent",
#     sub_agents=[ParallelResearchTeam],
#     max_iterations = 2,
# )