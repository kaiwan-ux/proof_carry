def get_runtime(name):
    if name=="langgraph":
        from .langgraph_runtime import LangGraphRuntime; return LangGraphRuntime()
    if name=="crewai":
        from .crewai_runtime import CrewAIRuntime; return CrewAIRuntime()
    if name=="maf":
        from .maf_runtime import MAFRuntime; return MAFRuntime()
    raise KeyError(name)
