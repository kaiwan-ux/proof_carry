from __future__ import annotations
import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
# Default integrated native run: ProofCarry only, all 120 cases, all five evidence conditions.
subprocess.run([sys.executable,str(ROOT/'scripts'/'run_native_full.py'),'--cases','all120','--profile','proofcarry','--variants','all'],cwd=ROOT,check=True)
run=(ROOT/'results'/'LATEST_NATIVE_RUN.txt').read_text(encoding='utf-8').strip()
subprocess.run([sys.executable,str(ROOT/'scripts'/'analyze_native_full.py'),run],cwd=ROOT,check=True)
subprocess.run([sys.executable,str(ROOT/'scripts'/'verify_native_full.py'),run],cwd=ROOT,check=True)
print('NativeFull ProofCarry run complete:',run)
