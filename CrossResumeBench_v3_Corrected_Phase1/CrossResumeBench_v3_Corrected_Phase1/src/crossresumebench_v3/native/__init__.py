from .langgraph_runtime import LangGraphRuntime
from .crewai_runtime import CrewAIRuntime
from .maf_runtime import MAFRuntime

def get_runtime(name):
    return {"langgraph":LangGraphRuntime,"crewai":CrewAIRuntime,"maf":MAFRuntime}[name]()
