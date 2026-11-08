from __future__ import annotations
import csv,json,hashlib,itertools,traceback
from pathlib import Path
from .models import RuntimeState
from .baselines import build_transfer,lower_transfer
from .adapters import get_adapter
from .evaluator import evaluate

def _rid(*p): return hashlib.sha256("|".join(map(str,p)).encode()).hexdigest()[:16]
def run_native(cases,frameworks,baselines,root:Path,adapter_getter=get_adapter):
    outdir=root/'results'/'native'; art=root/'results'/'artifacts'; outdir.mkdir(parents=True,exist_ok=True); art.mkdir(parents=True,exist_ok=True)
    rows=[]; tech=[]
    for src,tgt in itertools.permutations(frameworks,2):
        for case in cases:
            for b in baselines:
                run_id=_rid(src,tgt,case.case_id,b); pkg=build_transfer(b,case)
                if not pkg.accepted:
                    ev=evaluate(case,None,None,rejected=True); native=None; target=None; final=None
                else:
                    try:
                        imported=lower_transfer(pkg,case); final=dict(case.source_ledger); target,native=adapter_getter(tgt).run_target(case.family,imported,final); ev=evaluate(case,target,final)
                    except Exception as e:
                        tech.append({"run_id":run_id,"source":src,"target":tgt,"case_id":case.case_id,"baseline":b,"error":f"{type(e).__name__}: {e}","traceback":traceback.format_exc()});
                        rows.append({"run_id":run_id,"source_framework":src,"target_framework":tgt,"case_id":case.case_id,"family":case.family,"baseline":b,"safe_completion":0,"safe_rejection":0,"unsafe_violation":0,"technical_failure":1,"failure_types":"TECHNICAL_FAILURE","payload_bytes":pkg.byte_size(),"reject_reason":""}); continue
                rows.append({"run_id":run_id,"source_framework":src,"target_framework":tgt,"case_id":case.case_id,"family":case.family,"baseline":b,"safe_completion":ev.safe_completion,"safe_rejection":ev.safe_rejection,"unsafe_violation":ev.unsafe_violation,"technical_failure":0,"failure_types":";".join(ev.failure_types),"payload_bytes":pkg.byte_size(),"reject_reason":pkg.reject_reason or ""})
                (art/f"{run_id}.json").write_text(json.dumps({"case":case.to_dict(),"transfer":pkg.payload,"inference":pkg.inference_report,"native_target":native,"target_state":target.to_dict() if target else None,"final_ledger":final,"evaluation":ev.to_dict()},indent=2),encoding='utf-8')
    if rows:
        with (root/'results'/'native_runs.csv').open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    (root/'results'/'technical_failures.json').write_text(json.dumps(tech,indent=2),encoding='utf-8')
    return rows
