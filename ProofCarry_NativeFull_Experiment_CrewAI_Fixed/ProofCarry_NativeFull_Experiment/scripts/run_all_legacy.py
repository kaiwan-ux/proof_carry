from __future__ import annotations
import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
steps=['verify_package.py','verify_freeze.py','run_semantic.py','run_security.py','run_ablation.py','run_native.py','run_performance.py','analyze_results.py']
for s in steps:
    print('\n===',s,'===',flush=True)
    subprocess.run([sys.executable,str(ROOT/'scripts'/s)],cwd=ROOT,check=True)
