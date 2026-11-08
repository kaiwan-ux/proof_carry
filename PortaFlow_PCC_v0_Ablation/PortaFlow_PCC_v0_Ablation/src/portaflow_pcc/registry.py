from __future__ import annotations
from importlib import import_module

MODULES = {
    "langgraph": "portaflow_pcc.adapters.langgraph_adapter",
    "crewai": "portaflow_pcc.adapters.crewai_adapter",
    "maf": "portaflow_pcc.adapters.maf_adapter",
}

def adapter(name: str):
    if name not in MODULES:
        raise KeyError(name)
    return import_module(MODULES[name])
