from .langgraph_adapter import LangGraphAdapter
from .crewai_adapter import CrewAIAdapter
from .maf_adapter import MAFAgentAdapter

def get_adapter(name):
    return {"langgraph":LangGraphAdapter,"crewai":CrewAIAdapter,"maf":MAFAgentAdapter}[name]()
