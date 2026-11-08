from __future__ import annotations
import csv, hashlib, itertools, json, traceback
from pathlib import Path
from typing import Any
from .registry import adapter
from .models import SourceCapture, RunRecord, LogicalState
from .capsules import export_capsule, import_capsule
from .evaluator import evaluate


def _rid(parts): return hashlib.sha256("|".join(map(str,parts)).encode()).hexdigest()[:16]

def _json_default(x):
    if hasattr(x,"to_dict"): return x.to_dict()
    return str(x)

def run(config: dict[str,Any], root: Path) -> list[RunRecord]:
    res=root/"results"; (res/"native_sources").mkdir(parents=True,exist_ok=True); (res/"native_targets").mkdir(parents=True,exist_ok=True)
    frameworks=config["frameworks"]; workflows=config["workflows"]; conditions=config["conditions"]
    source_cache: dict[tuple[str,str],SourceCapture]={}
    technical=[]
    for src in frameworks:
        for wf in workflows:
            try:
                cap=adapter(src).run_source(wf); source_cache[(src,wf)]=cap
                (res/"native_sources"/f"{src}__{wf}.json").write_text(json.dumps(cap.to_dict(),indent=2,default=_json_default),encoding="utf-8")
            except Exception as e:
                technical.append({"stage":"source","framework":src,"workflow":wf,"error":f"{type(e).__name__}: {e}","traceback":traceback.format_exc()})
    records=[]; details=[]
    pairs=[p for p in itertools.product(frameworks,frameworks) if p[0]!=p[1]]
    for src,tgt in pairs:
        for wf in workflows:
            source=source_cache.get((src,wf))
            if source is None:
                for cond in conditions:
                    records.append(RunRecord(_rid([src,tgt,wf,cond]),src,tgt,wf,cond,0,1,"SOURCE_TECHNICAL_FAILURE",0,0,0,0,0,"missing",notes="source capture unavailable"))
                continue
            source_state=LogicalState.from_dict(source.state)
            for cond in conditions:
                rid=_rid([config["experiment_name"],src,tgt,wf,cond]); ledger=dict(source.external_ledger)
                try:
                    capsule=export_capsule(source,cond); imported=import_capsule(capsule)
                    target_state,target_native=adapter(tgt).run_target(wf,imported,ledger)
                    ev=evaluate(source_state,target_state,ledger)
                    rec=RunRecord(rid,src,tgt,wf,cond,int(ev["safe"]),0,";".join(ev["failure_types"]),ev["duplicate_effects"],ev["replayed_steps"],int(ev["approval_preserved"]),int(ev["retry_preserved"]),int(ev["correct_termination"]),source.native_snapshot.get("kind","unknown"))
                    records.append(rec)
                    detail={"run_id":rid,"source":source.to_dict(),"capsule":capsule,"target_framework":tgt,"target_state":target_state.to_dict(),"target_native":target_native,"final_ledger":ledger,"evaluation":ev}
                    details.append(detail)
                    (res/"native_targets"/f"{rid}.json").write_text(json.dumps(detail,indent=2,default=_json_default),encoding="utf-8")
                except Exception as e:
                    records.append(RunRecord(rid,src,tgt,wf,cond,0,1,"TARGET_TECHNICAL_FAILURE",0,0,0,0,0,source.native_snapshot.get("kind","unknown"),notes=f"{type(e).__name__}: {e}"))
                    technical.append({"stage":"target","source":src,"target":tgt,"workflow":wf,"condition":cond,"error":f"{type(e).__name__}: {e}","traceback":traceback.format_exc()})
    if records:
        with (res/"native_cross_runtime_runs.csv").open("w",newline="",encoding="utf-8") as f:
            wr=csv.DictWriter(f,fieldnames=list(records[0].to_dict())); wr.writeheader(); wr.writerows([r.to_dict() for r in records])
    (res/"technical_failures.json").write_text(json.dumps(technical,indent=2),encoding="utf-8")
    (res/"normalized_native_runs.jsonl").write_text("\n".join(json.dumps(x,sort_keys=True,default=_json_default) for x in details)+("\n" if details else ""),encoding="utf-8")
    return records
