"""Native validation entry point.

This script intentionally does NOT convert module importability into a scientific
"validated" claim. True native validation must execute source checkpoint capture,
self-resume, target reconstruction, and resume using the pinned framework APIs.

The previous passed 32-case native controls/source captures are preserved under
legacy_evidence/sealed_holdout_32. For the new 120-case benchmark, this script
records NOT_RUN until a framework-specific adapter is executed successfully.
"""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
from native.probe import run as probe

def main(root: Path, out: Path):
    probes=probe(out.with_suffix('.probe.json'))
    fields=['runtime','available','version','native_validation_status','reason']
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for p in probes:
            w.writerow({'runtime':p['runtime'],'available':p['available'],'version':p['version'],'native_validation_status':'NOT_RUN','reason':p['detail']})
    print('Native results are explicitly NOT_RUN. See docs/NATIVE_VALIDATION_PROTOCOL.md.')
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--out',default='results/native/native_validation.csv'); a=ap.parse_args(); main(Path(a.root),Path(a.out))
