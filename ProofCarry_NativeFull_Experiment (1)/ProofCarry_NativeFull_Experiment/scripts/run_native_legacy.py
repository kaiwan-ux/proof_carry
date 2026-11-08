import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path[:0]=[str(ROOT/'src'),str(ROOT/'frozen_v2'/'src'),str(ROOT)]
from crossresumebench_proofcarry.runner import native_study
result=native_study(ROOT/'results'); print(result)
if not result.get('native_gate_pass'): raise SystemExit(3)
