from pathlib import Path
import importlib.metadata
import json, os, sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"frozen_v2/src")]
from crossresumebench_v3_revb.native import get_runtime

cfg=json.loads((ROOT/"config/phase1_revisionB.json").read_text(encoding="utf-8"))
out={
    "python":sys.version,
    "frameworks":{},
    "installed_versions":{},
    "environment":{
        "CREWAI_TRACING_ENABLED":os.getenv("CREWAI_TRACING_ENABLED"),
        "CREWAI_DISABLE_TELEMETRY":os.getenv("CREWAI_DISABLE_TELEMETRY"),
        "CREWAI_DISABLE_TRACKING":os.getenv("CREWAI_DISABLE_TRACKING"),
        "OTEL_SDK_DISABLED":os.getenv("OTEL_SDK_DISABLED"),
    }
}
for pkg in ["langgraph","crewai","agent-framework-core"]:
    try: out["installed_versions"][pkg]=importlib.metadata.version(pkg)
    except importlib.metadata.PackageNotFoundError: out["installed_versions"][pkg]=None

for name in ["langgraph","crewai","maf"]:
    try: out["frameworks"][name]=get_runtime(name).capability_probe()
    except Exception as e: out["frameworks"][name]={"installed":False,"ready":False,"error":repr(e)}

(ROOT/"results").mkdir(exist_ok=True)
(ROOT/"results/capabilities.json").write_text(json.dumps(out,indent=2,default=str),encoding="utf-8")
print(json.dumps(out,indent=2,default=str))

errs=[]
if sys.version_info<(3,11): errs.append("Python 3.11+ required")
for pkg,exp in cfg["expected_versions"].items():
    got=out["installed_versions"].get(pkg)
    if got!=exp: errs.append(f"{pkg} version {got!r} != pinned {exp!r}")
for name,val in out["frameworks"].items():
    if not val.get("installed"): errs.append(f"{name} not installed")
    if val.get("ready") is False: errs.append(f"{name} missing required native capability")
if errs: raise SystemExit("PREFLIGHT FAIL: "+"; ".join(errs))
