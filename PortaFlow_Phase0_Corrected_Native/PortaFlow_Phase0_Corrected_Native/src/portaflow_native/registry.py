from __future__ import annotations
import importlib

MODULES={
    "langgraph":"portaflow_native.adapters.langgraph_adapter",
    "crewai":"portaflow_native.adapters.crewai_adapter",
    "maf":"portaflow_native.adapters.maf_adapter",
}

def adapter(name: str):
    if name not in MODULES: raise KeyError(name)
    return importlib.import_module(MODULES[name])
