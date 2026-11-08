from pathlib import Path
import sys,platform,json,importlib.metadata as md
ROOT=Path(__file__).resolve().parents[1]; pkgs={}
for p in ['langgraph','crewai','agent-framework-core','pydantic','pandas','matplotlib']:
    try: pkgs[p]=md.version(p)
    except Exception: pkgs[p]=None
(ROOT/'results/ENVIRONMENT.json').write_text(json.dumps({'python':sys.version,'platform':platform.platform(),'packages':pkgs},indent=2),encoding='utf-8')
