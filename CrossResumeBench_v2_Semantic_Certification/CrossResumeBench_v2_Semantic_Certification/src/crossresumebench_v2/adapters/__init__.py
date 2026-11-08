from .langgraph_adapter import LangGraphAdapter
from .crewai_adapter import CrewAIAdapter
from .maf_adapter import MAFAdapter
from .fake_adapter import FakeAdapter

def get_adapter(name):
    return {"langgraph":LangGraphAdapter,"crewai":CrewAIAdapter,"maf":MAFAdapter}[name]()
