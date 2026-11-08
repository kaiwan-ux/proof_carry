from __future__ import annotations
import json,csv,hashlib
from pathlib import Path
from .models import RuntimeState
from .baselines import build_transfer,lower_transfer
from .semantics import continue_case
from .evaluator import evaluate

def rid(*parts): return hashlib.sha256("|".join(map(str,parts)).encode()).hexdigest()[:16]

def run_suite(cases,baselines,results_dir:Path):
    results_dir.mkdir(parents=True,exist_ok=True); rows=[]
    for case in cases:
        for b in baselines:
            pkg=build_transfer(b,case); run_id=rid(case.case_id,b)
            if not pkg.accepted:
                ev=evaluate(case,None,None,rejected=True); final_ledger=None; target=None
            else:
                imported=lower_transfer(pkg,case); ledger=dict(case.source_ledger)
                target,final_ledger=continue_case(case.family,imported,ledger,oracle=(b=="oracle")); ev=evaluate(case,target,final_ledger)
            row={"run_id":run_id,"case_id":case.case_id,"family":case.family,"variant":case.variant,"baseline":b,"safe_completion":ev.safe_completion,"safe_rejection":ev.safe_rejection,"unsafe_violation":ev.unsafe_violation,"failure_types":";".join(ev.failure_types),"duplicate_effects":ev.duplicate_effects,"replayed_steps":ev.replayed_steps,"payload_bytes":pkg.byte_size(),"reject_reason":pkg.reject_reason or "","source_boundary":case.source_boundary,"target_boundary":case.target_boundary,"mismatch_tags":";".join(case.mismatch_tags)}
            rows.append(row)
            (results_dir/f"{run_id}.json").write_text(json.dumps({"case":case.to_dict(),"baseline":b,"transfer":pkg.payload,"inference":pkg.inference_report,"accepted":pkg.accepted,"reject_reason":pkg.reject_reason,"target":target.to_dict() if target else None,"final_ledger":final_ledger,"evaluation":ev.to_dict()},indent=2),encoding='utf-8')
    out=results_dir.parent/'semantic_runs.csv'
    with out.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    return rows
