import importlib,sys,json
mods=['pandas','matplotlib','pydantic','langgraph','crewai','agent_framework']; out={'python':sys.version,'modules':{}}
for m in mods:
    try: importlib.import_module(m); out['modules'][m]='ok'
    except Exception as e: out['modules'][m]=str(e)
print(json.dumps(out,indent=2)); raise SystemExit(0 if all(v=='ok' for v in out['modules'].values()) else 1)
