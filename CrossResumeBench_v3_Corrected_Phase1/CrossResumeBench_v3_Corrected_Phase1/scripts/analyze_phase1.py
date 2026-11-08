from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from crossresumebench_v3.analysis import analyze
print(json.dumps(analyze(ROOT/'results'),indent=2))
