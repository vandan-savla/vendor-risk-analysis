from google.adk.agents import Agent, ParallelAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search
from google.genai import types

retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504], # Retry on these HTTP errors
)


BreachSearchAgent = Agent(
    name="BreachSearchAgent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config
    ),
    instruction="""
        You are a Cybersecurity Breach Research Specialist.

        Inputs:
        - vendor_name = vendor_name
        - website_url = website_url
        - search_enabled = {orchestrator_agent_result.breach_agent}
        - guided_queries = {orchestrator_agent_result.breach_queries}

        Behavior:
        - If search_enabled is false -> do NOT perform any search. 
        Immediately return: "No requirement given for breach-related search."
        - If true -> begin with guided_queries, then expand outward ONLY within relevant cybersecurity sources.

        =====================
        ### SEARCH SCOPE
        Focus strictly on:
        - Confirmed or reported data breaches
        - Ransomware attacks
        - Hacking incidents affecting vendor systems/products
        - Public vulnerability disclosures (CVEs)
        - Mentions in:
        - Security news outlets
        - Cybersecurity blogs
        - Reddit communities (e.g., r/cybersecurity, r/netsec)
        - Hacker forum archives (via Google Search only)
        - Government breach reporting portals

        Never invent events. Only report findings you can trace to a credible source.

        =====================
        ### Needed Information as output along with anything that seems necessary.
        Return a structured factual summary:
        - incident_type
        - date (if available)
        - severity (low / medium / high)
        - short description
        - source_urls (list)
        - status (resolved / ongoing / unclear)
        - Cite the sources Positive ones as well

        If absolutely nothing relevant is found -> return:
        "No breach-related public signals detected."
    """,
    tools=[google_search],
    output_key="breach_search_results"
)


LegalSearchAgent = Agent(
    name="LegalSearchAgent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config
    ),
    instruction="""
        You are a Legal & Regulatory Risk Research Specialist.

        Inputs:
        - vendor_name = vendor_name
        - website_url = website_url
        - search_enabled = {orchestrator_agent_result.legal_agent}
        - guided_queries = {orchestrator_agent_result.legal_queries}

        Behavior:
        - If search_enabled is false -> return: "No requirement given for legal search."
        - If true -> begin with guided_queries, then expand search strictly within legal/regulatory sources.

        =====================
        ### SEARCH SCOPE
        Look ONLY for:
        - Lawsuits (past or ongoing)
        - Class-action filings
        - Regulatory fines or penalties (GDPR, FTC, SEC, CCI, ICO, etc.)
        - Consumer protection complaints
        - Violations involving:
        - parent company
        - subsidiaries
        - major corporate entities associated with vendor
        - Court filings or judgments
        - Credible press and compliance reports

        Do NOT infer guilt. Only cite what the public record confirms.

        =====================
        ### Needed Information as output along with anything that seems necessary.
        Return a structured list:
        - issue_type
        - severity (low / medium / high)
        - court_or_regulator
        - date (if known)
        - summary
        - source_urls (list)
        - Cite the sources Positive ones as well

        If no findings -> return:
        "No public legal or regulatory issues detected."
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
    instruction="""
        You are a Financial Stability Risk Research Analyst.

        Inputs:
        - vendor_name = vendor_name
        - website_url = website_url
        - search_enabled = {orchestrator_agent_result.financial_agent}
        - guided_queries = {orchestrator_agent_result.financial_queries}

        Behavior:
        - If search_enabled is false -> return: "No requirement given for financial search."
        - If true -> start with guided_queries, then expand search cautiously across credible financial sources.

        =====================
        ### SEARCH SCOPE
        Check for:
        - Bankruptcy risk indicators
        - Large-scale fraud investigations
        - Funding problems / withdrawn investments
        - Market trust issues
        - Major revenue decline signals
        - Analyst reviews / investor commentary
        - Customer complaints related to service quality impacting financial posture

        Avoid unverified rumors. Stick to reports with identifiable sources.

        =====================
        ### Needed Information as output along with anything that seems necessary.
        Return structured findings:
        - category (fraud / layoffs / bankruptcy / funding issues / etc.)
        - severity (low / medium / high)
        - timeframe (recent / historical)
        - short description
        - source_urls (list)
        - Cite the sources Positive ones as well

        If nothing credible found:
        "No public financial warning signs detected."
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
        You are a Compliance Certificate Researcher.

        Inputs:
        - vendor_name = vendor_name
        - website_url = website_url
        - search_enabled = {orchestrator_agent_result.compliance_agent}
        - guided_queries = {orchestrator_agent_result.compliance_queries}

        Behavior:
        - If search_enabled is false -> return: "No requirement given for compliance search."
        - If true -> start with guided_queries, then expand only into certification-relevant sources.

        =====================
        ### SEARCH SCOPE
        
        Determine if vendor has taken compliance certifications 
        The certifications information can be found at privacy policy, terms of use, trust centers or security pages of the vendor_name.
        The result must include the urls of the certificates.
        
        The compliance certifications must be relavant to the purpose for which vendor is being onboarded purpose_of_onboarding, the kind of data is processed.
        For example if the vendor is handling medical information it must be HIPPA compliant. The certification mention can be found publicly on their website_url or trust center.
        
        If the certifications mentions are found consider it a success; no need for verification since it is private to their organization. 
        
        The ratings must be given based on the 
        1. purpose_of_onboarding
        2. Kind of data vendor is going to process
        3. Whether relevant certifications are needed and present.
            
        =====================
        ### Needed Information as output along with anything that seems necessary.
        Return structured findings:
        - evidence_urls (list)
        - missing_or_red_flags (list)
        - severity_of_gap (low / medium / high)
        - Cite the sources Positive ones as well

        If you cannot verify anything:
        "Insufficient public evidence to confirm vendor compliance posture."
    """,
    
    tools=[google_search],
    output_key="compliance_search_results",
)

# Parallel Research Team - Invokes all the research agents in parallel, reducing lateny.
ParallelResearchTeam = ParallelAgent(
    name="ParallelResearchTeam",
    sub_agents=[BreachSearchAgent,LegalSearchAgent,FinancialSearchAgent, ComplianceSearchAgent],
)

