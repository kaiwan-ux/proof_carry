from __future__ import annotations
import csv,hashlib,itertools,json,traceback
from pathlib import Path
from typing import Any,Callable
from .models import SourceCapture,RunRecord,ExecutionState
from .pcc import build_capsule,lower_capsule
from .evaluator import evaluate
from .registry import adapter as default_adapter
from .benchmark import STATIC_SPECS

def _rid(parts): return hashlib.sha256("|".join(map(str,parts)).encode()).hexdigest()[:16]
def _jd(x): return x.to_dict() if hasattr(x,"to_dict") else str(x)

def run(config:dict[str,Any],root:Path,adapter_getter:Callable[[str],Any]=default_adapter):
    res=root/"results"
    for d in ["native_sources","native_targets","capsules","inference_reports"]:(res/d).mkdir(parents=True,exist_ok=True)
    frameworks=config["frameworks"]; workflows=config["workflows"]; conditions=config["conditions"]
    (res/"STATIC_WORKFLOW_SPECS.json").write_text(json.dumps({k:STATIC_SPECS[k] for k in workflows},indent=2),encoding="utf-8")
    cache={}; technical=[]
    for src in frameworks:
        for wf in workflows:
            try:
                c=adapter_getter(src).run_source(wf); cache[(src,wf)]=c
                (res/"native_sources"/f"{src}__{wf}.json").write_text(json.dumps(c.to_dict(),indent=2,default=_jd),encoding="utf-8")
            except Exception as e: technical.append({"stage":"source","framework":src,"workflow":wf,"error":f"{type(e).__name__}: {e}","traceback":traceback.format_exc()})
    records=[]; details=[]
    for src,tgt in [p for p in itertools.product(frameworks,frameworks) if p[0]!=p[1]]:
        for wf in workflows:
            source=cache.get((src,wf))
            for cond in conditions:
                rid=_rid([config["experiment_name"],src,tgt,wf,cond])
                if source is None:
                    records.append(RunRecord(rid,src,tgt,wf,cond,0,0,0,1,"SOURCE_TECHNICAL_FAILURE",0,0,0,0,0,0,0,0,"missing","source unavailable")); continue
                try:
                    cap=build_capsule(source,cond); capd=cap.to_dict(); blob=json.dumps(capd)
                    for forbidden in ["native_snapshot","latest_checkpoint","flow_id","checkpoint_id"]:
                        if f'"{forbidden}"' in blob: raise AssertionError(f"PCC leaked forbidden native field: {forbidden}")
                    imported,irep,accepted,reject_reason=lower_capsule(cap)
                    (res/"capsules"/f"{rid}.json").write_text(json.dumps(capd,indent=2),encoding="utf-8")
                    (res/"inference_reports"/f"{rid}.json").write_text(json.dumps({**irep,"accepted":accepted,"reject_reason":reject_reason},indent=2),encoding="utf-8")
                    if not accepted:
                        records.append(RunRecord(rid,src,tgt,wf,cond,0,1,0,0,reject_reason or "REJECTED",len(irep.get("ambiguities",[])),len(irep.get("inferred_fields",[])),cap.byte_size(),0,0,0,0,0,source.native_snapshot.get("kind","unknown"),"safe rejection by inference baseline")); continue
                    ledger=dict(source.external_ledger); initial_trace_len=len(imported.trace)
                    target,target_native=adapter_getter(tgt).run_target(wf,imported,ledger)
                    ev=evaluate(ExecutionState.from_dict(source.state),target,initial_trace_len,ledger,source.external_ledger)
                    rec=RunRecord(rid,src,tgt,wf,cond,int(ev["safe"]),0,int(not ev["safe"]),0,";".join(ev["failure_types"]),len(irep.get("ambiguities",[])),len(irep.get("inferred_fields",[])),cap.byte_size(),ev["duplicate_effects"],ev["replayed_steps"],ev["wrong_outcome"],ev["wrong_ledger"],ev["wrong_trace"],source.native_snapshot.get("kind","unknown"))
                    records.append(rec)
                    detail={"run_id":rid,"source":source.to_dict(),"capsule":capd,"inference":irep,"target_framework":tgt,"target_state":target.to_dict(),"target_native":target_native,"final_ledger":ledger,"evaluation":ev}
                    details.append(detail); (res/"native_targets"/f"{rid}.json").write_text(json.dumps(detail,indent=2,default=_jd),encoding="utf-8")
                except Exception as e:
                    records.append(RunRecord(rid,src,tgt,wf,cond,0,0,0,1,"TARGET_TECHNICAL_FAILURE",0,0,0,0,0,0,0,0,source.native_snapshot.get("kind","unknown"),f"{type(e).__name__}: {e}")); technical.append({"stage":"target","source":src,"target":tgt,"workflow":wf,"condition":cond,"error":f"{type(e).__name__}: {e}","traceback":traceback.format_exc()})
    if records:
        with (res/"generalization_runs.csv").open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=list(records[0].to_dict())); w.writeheader(); w.writerows([r.to_dict() for r in records])
    (res/"technical_failures.json").write_text(json.dumps(technical,indent=2),encoding="utf-8")
    (res/"normalized_runs.jsonl").write_text("\n".join(json.dumps(x,sort_keys=True,default=_jd) for x in details)+("\n" if details else ""),encoding="utf-8")
    return records
