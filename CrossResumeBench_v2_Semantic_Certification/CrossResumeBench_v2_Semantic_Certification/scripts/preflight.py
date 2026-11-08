from pathlib import Path
import importlib.util,json,sys,platform
ROOT=Path(__file__).resolve().parents[1]; req={"langgraph":"langgraph","crewai":"crewai","maf":"agent_framework","pandas":"pandas","jsonschema":"jsonschema"}; missing=[k for k,m in req.items() if importlib.util.find_spec(m) is None]; out={"python":sys.version,"platform":platform.platform(),"required":req,"missing":missing,"ok":not missing}; (ROOT/'results'/'PREFLIGHT.json').write_text(json.dumps(out,indent=2)); print(json.dumps(out,indent=2)); sys.exit(1 if missing else 0)
