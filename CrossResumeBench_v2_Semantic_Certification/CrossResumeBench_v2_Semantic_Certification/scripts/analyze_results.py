from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src')); from crossresumebench_v2.analysis import summarize; print(json.dumps(summarize(ROOT),indent=2,default=str))
