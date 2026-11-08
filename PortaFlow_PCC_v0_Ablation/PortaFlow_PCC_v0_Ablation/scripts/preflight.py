from pathlib import Path
import importlib, importlib.metadata, json, platform, sys
ROOT=Path(__file__).resolve().parents[1]; RES=ROOT/'results'; RES.mkdir(exist_ok=True)
mods=['langgraph','crewai','agent_framework','pydantic','pandas','matplotlib','pytest']
out={'python':sys.version,'platform':platform.platform(),'modules':{},'ok':True}
for m in mods:
    try:
        importlib.import_module(m)
        dist={'langgraph':'langgraph','crewai':'crewai','agent_framework':'agent-framework-core'}.get(m,m)
        try: v=importlib.metadata.version(dist)
        except Exception: v=None
        out['modules'][m]={'ok':True,'version':v}
    except Exception as e:
        out['modules'][m]={'ok':False,'error':f'{type(e).__name__}: {e}'}; out['ok']=False
(RES/'PREFLIGHT.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
if not out['ok']: raise SystemExit(2)
