import json,platform,subprocess,sys
from importlib import metadata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ps={}
for x in ["langgraph","crewai","agent-framework-core","pydantic","pandas","matplotlib","pytest"]:
    try: ps[x]=metadata.version(x)
    except Exception: ps[x]=None
obj={"python":sys.version,"platform":platform.platform(),"packages":ps}
(ROOT/"results"/"ENVIRONMENT.json").write_text(json.dumps(obj,indent=2),encoding="utf-8")
print("Environment captured.")
