from __future__ import annotations
import json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path[:0]=[str(ROOT/'src'),str(ROOT/'frozen_v2'/'src'),str(ROOT)]
from crossresumebench_mccv3.runner import run
from crossresumebench_mccv3.infra.isolated_runtime import isolated_runtime_factory

def main():
    gate=ROOT/'native_gate_results'/'NATIVE_FAMILY_GATE.json'
    if not gate.exists(): raise SystemExit('native gate result missing; run scripts/native_gate_infrafixA.py first')
    g=json.loads(gate.read_text(encoding='utf-8'))
    if not g.get('pass'): raise SystemExit('native gate did not pass; full holdout intentionally not started')
    result=run(ROOT/'results',runtime_factory=isolated_runtime_factory,skip_native_gate=True)
    # Preserve the separate pre-gate proof in the final results archive.
    (ROOT/'results'/'native_gate').mkdir(parents=True,exist_ok=True)
    for name in ['NATIVE_FAMILY_GATE.json','native_family_gate.csv']:
        shutil.copy2(ROOT/'native_gate_results'/name,ROOT/'results'/'native_gate'/name)
    print(result)
if __name__=='__main__': main()
