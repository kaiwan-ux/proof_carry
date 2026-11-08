from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]; sys.path[:0]=[str(ROOT/"src"),str(ROOT/"frozen_v2"/"src")]
from crossresumebench_v3_full.analysis import analyze
print(json.dumps(analyze(ROOT/"results"),indent=2))
