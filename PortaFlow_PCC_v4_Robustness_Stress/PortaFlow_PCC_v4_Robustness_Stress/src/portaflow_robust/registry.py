from __future__ import annotations
import importlib
def adapter(name:str):
    return importlib.import_module(f"portaflow_robust.adapters.{name}_adapter")
