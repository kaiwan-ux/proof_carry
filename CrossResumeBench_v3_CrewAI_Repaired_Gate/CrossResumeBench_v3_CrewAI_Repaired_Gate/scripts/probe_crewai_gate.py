
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"frozen_v2/src")]
from crossresumebench_crewai_gate.probe import run_probe
r=run_probe(ROOT/"results")
print(json.dumps(r,indent=2,default=str))
raise SystemExit(0 if r["probe_pass"] else 2)
