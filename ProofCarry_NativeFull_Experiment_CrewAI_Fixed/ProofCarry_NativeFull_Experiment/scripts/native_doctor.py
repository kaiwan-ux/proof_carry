from __future__ import annotations
import argparse, json, platform, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from crossresumebench_proofcarry.native_full_study import capability_doctor

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',default='results/native_full')
    args=ap.parse_args(); out=ROOT/args.out; out.mkdir(parents=True,exist_ok=True)
    rows=capability_doctor(out)
    env={'python':sys.version,'platform':platform.platform(),'executable':sys.executable,'frameworks':rows}
    (out/'NATIVE_ENVIRONMENT_DOCTOR.json').write_text(json.dumps(env,indent=2,sort_keys=True,default=str),encoding='utf-8')
    print(json.dumps(env,indent=2,default=str))
    return 0 if all(int(r['ready']) for r in rows) else 2
if __name__=='__main__': raise SystemExit(main())
