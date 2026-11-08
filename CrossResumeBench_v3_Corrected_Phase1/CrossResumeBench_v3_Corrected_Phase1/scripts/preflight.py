from importlib import import_module,metadata
from pathlib import Path
import json,sys,os
ROOT=Path(__file__).resolve().parents[1]; sys.path[:0]=[str(ROOT/'src'),str(ROOT/'frozen_v2/src')]
from crossresumebench_v3.native import get_runtime
out={"python":sys.version,"frameworks":{},"environment":{"CREWAI_TRACING_ENABLED":os.getenv('CREWAI_TRACING_ENABLED'),"OTEL_SDK_DISABLED":os.getenv('OTEL_SDK_DISABLED')}}
for name in ['langgraph','crewai','maf']:
    try: out['frameworks'][name]=get_runtime(name).capability_probe()
    except Exception as e: out['frameworks'][name]={"installed":False,"error":repr(e)}
(ROOT/'results').mkdir(exist_ok=True); (ROOT/'results/capabilities.json').write_text(json.dumps(out,indent=2,default=str))
print(json.dumps(out,indent=2,default=str))
if not all(v.get('installed') for v in out['frameworks'].values()): raise SystemExit(2)
