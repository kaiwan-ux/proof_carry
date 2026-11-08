from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"frozen_v2/src")]
from crossresumebench_v3_revc.analysis import analyze
v=analyze(ROOT/"results")
print(json.dumps(v,indent=2))
