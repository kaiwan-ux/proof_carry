from __future__ import annotations
import itertools,csv,json,hashlib,traceback
from pathlib import Path
from .baselines.core import build_transfer,lower_transfer
from .evaluator import evaluate
from .adapters import get_adapter

def _rid(*x): return hashlib.sha256("|".join(map(str,x)).encode()).hexdigest()[:16]

def run_native(cases,frameworks,baselines,root:Path,adapter_getter=get_adapter):
    rows=[]; failures=[]; srcdir=root/'results'/'native_sources'; tgtdir=root/'results'/'native_targets'; art=root/'results'/'artifacts'; srcdir.mkdir(parents=True,exist_ok=True); tgtdir.mkdir(parents=True,exist_ok=True); art.mkdir(parents=True,exist_ok=True)
    # Critical correction from v1: source framework is actually invoked and its capture is reused for all targets.
    captures={}
    for src in frameworks:
        ad=adapter_getter(src)
        for case in cases:
            try:
                cap=ad.capture_source(case); captures[(src,case.case_id)]=cap
                (srcdir/f"{src}__{case.case_id}.json").write_text(json.dumps(cap.to_dict(),indent=2),encoding='utf-8')
            except Exception as e:
                failures.append({"stage":"source_capture","source":src,"case_id":case.case_id,"error":f"{type(e).__name__}: {e}","traceback":traceback.format_exc()})
    for src,tgt in itertools.permutations(frameworks,2):
        tad=adapter_getter(tgt)
        for case in cases:
            cap=captures.get((src,case.case_id))
            for b in baselines:
                run_id=_rid(src,tgt,case.case_id,b)
                if cap is None:
                    rows.append({"run_id":run_id,"source_framework":src,"target_framework":tgt,"case_id":case.case_id,"family":case.family,"baseline":b,"safe_completion":0,"safe_rejection":0,"unsafe_violation":0,"technical_failure":1,"failure_types":"SOURCE_CAPTURE_FAILED","payload_bytes":0,"reject_reason":""}); continue
                try:
                    pkg=build_transfer(b,cap,case,tgt,root); rc=lower_transfer(pkg,cap,case,root)
                    if not pkg.accepted:
                        ev=evaluate(case,cap,None,True); target=None
                    else:
                        target=tad.run_target(case,rc,dict(cap.source_ledger)); ev=evaluate(case,cap,target)
                        (tgtdir/f"{run_id}.json").write_text(json.dumps(target.to_dict(),indent=2),encoding='utf-8')
                    rows.append({"run_id":run_id,"source_framework":src,"target_framework":tgt,"case_id":case.case_id,"family":case.family,"baseline":b,"safe_completion":ev.safe_completion,"safe_rejection":ev.safe_rejection,"unsafe_violation":ev.unsafe_violation,"technical_failure":0,"failure_types":";".join(ev.failure_types),"payload_bytes":pkg.byte_size(),"reject_reason":pkg.reject_reason or ""})
                    (art/f"{run_id}.json").write_text(json.dumps({"source_capture":cap.to_dict(),"transfer":pkg.payload,"inference":pkg.inference_report,"target":target.to_dict() if target else None,"evaluation":ev.to_dict()},indent=2),encoding='utf-8')
                except Exception as e:
                    failures.append({"stage":"target","run_id":run_id,"source":src,"target":tgt,"case_id":case.case_id,"baseline":b,"error":f"{type(e).__name__}: {e}","traceback":traceback.format_exc()}); rows.append({"run_id":run_id,"source_framework":src,"target_framework":tgt,"case_id":case.case_id,"family":case.family,"baseline":b,"safe_completion":0,"safe_rejection":0,"unsafe_violation":0,"technical_failure":1,"failure_types":"TECHNICAL_FAILURE","payload_bytes":0,"reject_reason":""})
    with (root/'results'/'native_runs.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    (root/'results'/'technical_failures.json').write_text(json.dumps(failures,indent=2),encoding='utf-8')
    return rows
