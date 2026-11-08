from __future__ import annotations
import importlib, json
from pathlib import Path
from .base import NativeProbe
MODULES={'langgraph':'langgraph','crewai':'crewai','maf':'agent_framework'}

def probe_one(runtime):
    m=MODULES[runtime]
    try:
        mod=importlib.import_module(m); version=getattr(mod,'__version__','installed-version-unknown')
        return NativeProbe(runtime,True,str(version),False,False,False,'DEPENDENCY_AVAILABLE_NOT_YET_EXECUTED','Run native/run_native_validation.py in the pinned environment; availability alone is not validation.')
    except Exception as e:
        return NativeProbe(runtime,False,'NOT_INSTALLED',False,False,False,'NOT_RUN_DEPENDENCY_MISSING',f'{type(e).__name__}: {e}')

def run(out: Path):
    rows=[probe_one(r).to_dict() for r in ['langgraph','crewai','maf']]
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(rows,indent=2),encoding='utf-8'); return rows
if __name__=='__main__':
    import argparse; ap=argparse.ArgumentParser(); ap.add_argument('--out',default='results/native/native_probe.json'); a=ap.parse_args(); run(Path(a.out))
