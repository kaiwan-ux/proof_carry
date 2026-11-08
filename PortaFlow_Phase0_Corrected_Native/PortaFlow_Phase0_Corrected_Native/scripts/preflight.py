from pathlib import Path
import importlib.metadata as md, json, platform, sys
ROOT=Path(__file__).resolve().parents[1]
packages={}
for dist in ["langgraph","crewai","agent-framework-core","pydantic","pandas","matplotlib"]:
    try: packages[dist]=md.version(dist)
    except Exception: packages[dist]=None
payload={"python":sys.version,"platform":platform.platform(),"packages":packages,
         "required_ok":all(packages[x] for x in ["langgraph","crewai","agent-framework-core"])}
(ROOT/"results/PREFLIGHT.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
print(json.dumps(payload,indent=2))
if not payload["required_ok"]: raise SystemExit(2)
