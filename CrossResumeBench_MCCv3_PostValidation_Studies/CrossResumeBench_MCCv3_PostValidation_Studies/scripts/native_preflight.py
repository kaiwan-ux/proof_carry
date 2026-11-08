import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path[:0]=[str(ROOT/'src'),str(ROOT/'frozen_v2'/'src'),str(ROOT)]
mods=['langgraph','crewai','agent_framework','jsonschema','pandas','pydantic']
for m in mods:
    x=__import__(m); print(m,getattr(x,'__version__','unknown'))
from crossresumebench_mccv3.native import get_runtime
for n in ['langgraph','crewai','maf']: print(get_runtime(n).capability_probe())
