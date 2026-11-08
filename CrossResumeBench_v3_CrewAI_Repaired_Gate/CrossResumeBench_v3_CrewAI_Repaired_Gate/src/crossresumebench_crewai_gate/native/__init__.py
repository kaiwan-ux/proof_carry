from .crewai_runtime import CrewAIRuntime

def get_runtime(name: str = "crewai"):
    if name != "crewai":
        raise KeyError(f"CrewAI-only gate: unsupported runtime {name!r}")
    return CrewAIRuntime()
