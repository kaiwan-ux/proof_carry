import json,platform,sys
from importlib import metadata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
packages={}
for dist in ["langgraph","crewai","agent-framework-core","pydantic","pandas","matplotlib"]:
    try: packages[dist]=metadata.version(dist)
    except metadata.PackageNotFoundError: packages[dist]=None
info={"python":sys.version,"platform":platform.platform(),"packages":packages}
(ROOT/"results"/"PREFLIGHT.json").write_text(json.dumps(info,indent=2),encoding="utf-8")
missing=[k for k,v in packages.items() if v is None and k in {"langgraph","crewai","agent-framework-core"}]
print(json.dumps(info,indent=2))
if missing: raise SystemExit("Missing required native framework packages: "+", ".join(missing))
