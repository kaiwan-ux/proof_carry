from __future__ import annotations
import importlib.metadata as md, json, platform, sys
EXPECTED={"langgraph":"1.2.11","crewai":"1.15.17","agent-framework-core":"1.15.0"}
found={}; bad=[]
for p,v in EXPECTED.items():
    try: found[p]=md.version(p)
    except Exception: found[p]=None
    if found[p]!=v: bad.append(f"{p}: expected {v}, found {found[p]}")
print(json.dumps({"python":sys.version,"platform":platform.platform(),"packages":found,"ok":not bad,"problems":bad},indent=2))
raise SystemExit(0 if not bad else 2)
