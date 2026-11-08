
from pathlib import Path
import importlib.metadata, json, os, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"frozen_v2/src")]
from crossresumebench_crewai_gate.native import get_runtime
cfg=json.loads((ROOT/"config/crewai_gate.json").read_text(encoding="utf-8"))
out={"python":sys.version,"installed_versions":{},"environment":{},"crewai_capability":{}}
for pkg in ["crewai","pydantic","jsonschema","pandas"]:
    try: out["installed_versions"][pkg]=importlib.metadata.version(pkg)
    except importlib.metadata.PackageNotFoundError: out["installed_versions"][pkg]=None
for k in ["CREWAI_TRACING_ENABLED","CREWAI_DISABLE_TELEMETRY","CREWAI_DISABLE_TRACKING","OTEL_SDK_DISABLED"]:
    out["environment"][k]=os.getenv(k)
try: out["crewai_capability"]=get_runtime("crewai").capability_probe()
except Exception as e: out["crewai_capability"]={"ready":False,"error":repr(e)}
(ROOT/"results").mkdir(exist_ok=True)
(ROOT/"results/capabilities.json").write_text(json.dumps(out,indent=2,default=str),encoding="utf-8")
print(json.dumps(out,indent=2,default=str))
errs=[]
if sys.version_info<(3,11): errs.append("Python 3.11+ required")
if out["installed_versions"].get("crewai")!=cfg["expected_versions"]["crewai"]:
    errs.append(f"crewai version {out['installed_versions'].get('crewai')!r} != pinned {cfg['expected_versions']['crewai']!r}")
if not out["crewai_capability"].get("ready"): errs.append("CrewAI required checkpoint capability not ready")
if errs: raise SystemExit("PREFLIGHT FAIL: "+"; ".join(errs))
print("PASS: CrewAI-only preflight")
