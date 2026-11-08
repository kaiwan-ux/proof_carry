from __future__ import annotations
import csv,json,hashlib
from pathlib import Path
from .source_engine import simulate_source
from .baselines.core import build_transfer,lower_transfer
from .target_engine import execute_target
from .evaluator import evaluate

def rid(*x): return hashlib.sha256("|".join(map(str,x)).encode()).hexdigest()[:16]

def run_semantic(cases,baselines,root:Path):
    rows=[]; art=root/'results'/'artifacts'; art.mkdir(parents=True,exist_ok=True)
    for case in cases:
        capture=simulate_source(case)
        for b in baselines:
            pkg=build_transfer(b,capture,case,"semantic",root); rc=lower_transfer(pkg,capture,case,root)
            if not pkg.accepted:
                ev=evaluate(case,capture,None,True); target=None
            else:
                target=execute_target(case,rc,dict(capture.source_ledger)); ev=evaluate(case,capture,target)
            run_id=rid("semantic",case.case_id,b)
            rows.append({"run_id":run_id,"case_id":case.case_id,"family":case.family,"baseline":b,"safe_completion":ev.safe_completion,"safe_rejection":ev.safe_rejection,"unsafe_violation":ev.unsafe_violation,"failure_types":";".join(ev.failure_types),"payload_bytes":pkg.byte_size(),"reject_reason":pkg.reject_reason or "","technical_failure":0})
            (art/f"{run_id}.json").write_text(json.dumps({"case":case.to_dict(),"source_capture":capture.to_dict(),"transfer":pkg.payload,"inference":pkg.inference_report,"target":target.to_dict() if target else None,"evaluation":ev.to_dict()},indent=2),encoding='utf-8')
    with (root/'results'/'semantic_runs.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    return rows
