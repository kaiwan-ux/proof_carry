from __future__ import annotations
import csv, json, hashlib, itertools, traceback
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Any, Callable
from .models import ExecutionState
from .capsule import build_capsule, lower_capsule
from .evaluator import evaluate
from .registry import adapter as default_adapter
from .components import subset_key

@dataclass
class NativeRow:
    run_id:str; source_framework:str; target_framework:str; workflow:str; condition:str; inference_mode:str
    subset_key:str; components:str; component_count:int; safe_completion:int; migration_rejected:int; unsafe_violation:int; technical_failure:int
    failure_types:str; ambiguity_count:int; inferred_fields:int; capsule_bytes:int; duplicate_effects:int; replayed_steps:int; wrong_outcome:int; wrong_ledger:int; wrong_trace:int; source_snapshot_kind:str; notes:str=""
    def to_dict(self): return asdict(self)

def _rid(parts): return hashlib.sha256("|".join(map(str,parts)).encode()).hexdigest()[:16]
def _jd(x): return x.to_dict() if hasattr(x,"to_dict") else str(x)
def _safe_filename(value:str)->str: return value.replace("::","__")

def run_native(config:dict[str,Any], root:Path, selected:list[dict[str,Any]], adapter_getter:Callable[[str],Any]=default_adapter):
    R=root/'results'
    for d in ['native_sources','native_targets','capsules','inference_reports']:(R/d).mkdir(parents=True,exist_ok=True)
    frameworks=config['frameworks']; workflows=config['workflows']; technical=[]; cache={}
    for src in frameworks:
        for wf in workflows:
            try:
                c=adapter_getter(src).run_source(wf); cache[(src,wf)]=c
                (R/'native_sources'/f'{src}__{_safe_filename(wf)}.json').write_text(json.dumps(c.to_dict(),indent=2,default=_jd),encoding='utf-8')
            except Exception as e:
                technical.append({'stage':'source','framework':src,'workflow':wf,'error':f'{type(e).__name__}: {e}','traceback':traceback.format_exc()})
    rows=[]
    pairs=[p for p in itertools.product(frameworks,frameworks) if p[0]!=p[1]]
    for src,tgt in pairs:
        for wf in workflows:
            source=cache.get((src,wf))
            for cond in selected:
                name=cond['name']; comps=tuple(cond['components']); mode=cond['inference_mode']; rid=_rid([config['experiment_name'],src,tgt,wf,name])
                if source is None:
                    rows.append(NativeRow(rid,src,tgt,wf,name,mode,subset_key(comps),','.join(comps),len(comps),0,0,0,1,'SOURCE_TECHNICAL_FAILURE',0,0,0,0,0,0,0,0,'missing','source unavailable')); continue
                try:
                    cap=build_capsule(source,comps,mode); capd=cap.to_dict(); blob=json.dumps(capd)
                    for forbidden in ['"native_snapshot"','"latest_checkpoint"','"checkpoint_id"','"flow_id"']:
                        if forbidden in blob: raise AssertionError(f'PCC leaked forbidden native field: {forbidden}')
                    imported,rep,accepted,reason=lower_capsule(cap)
                    (R/'capsules'/f'{rid}.json').write_text(json.dumps(capd,indent=2),encoding='utf-8')
                    (R/'inference_reports'/f'{rid}.json').write_text(json.dumps({**rep,'accepted':accepted,'reject_reason':reason},indent=2),encoding='utf-8')
                    if not accepted:
                        rows.append(NativeRow(rid,src,tgt,wf,name,mode,subset_key(comps),','.join(comps),len(comps),0,1,0,0,reason or 'REJECTED',len(rep.get('ambiguities',[])),len(rep.get('inferred_fields',[])),cap.byte_size(),0,0,0,0,0,source.native_snapshot.get('kind','unknown'),'safe rejection before target execution')); continue
                    ledger=dict(source.external_ledger); initial_len=len(imported.trace)
                    target,native=adapter_getter(tgt).run_target(wf,imported,ledger)
                    ev=evaluate(ExecutionState.from_dict(source.state),target,initial_len,ledger,source.external_ledger)
                    row=NativeRow(rid,src,tgt,wf,name,mode,subset_key(comps),','.join(comps),len(comps),int(ev['safe']),0,int(not ev['safe']),0,';'.join(ev['failure_types']),len(rep.get('ambiguities',[])),len(rep.get('inferred_fields',[])),cap.byte_size(),ev['duplicate_effects'],ev['replayed_steps'],ev['wrong_outcome'],ev['wrong_ledger'],ev['wrong_trace'],source.native_snapshot.get('kind','unknown'))
                    rows.append(row)
                    detail={'run_id':rid,'source':source.to_dict(),'condition':cond,'capsule':capd,'inference':rep,'target_framework':tgt,'target_state':target.to_dict(),'target_native':native,'final_ledger':ledger,'evaluation':ev}
                    (R/'native_targets'/f'{rid}.json').write_text(json.dumps(detail,indent=2,default=_jd),encoding='utf-8')
                except Exception as e:
                    rows.append(NativeRow(rid,src,tgt,wf,name,mode,subset_key(comps),','.join(comps),len(comps),0,0,0,1,'TARGET_TECHNICAL_FAILURE',0,0,0,0,0,0,0,0,source.native_snapshot.get('kind','unknown'),f'{type(e).__name__}: {e}'))
                    technical.append({'stage':'target','source':src,'target':tgt,'workflow':wf,'condition':name,'error':f'{type(e).__name__}: {e}','traceback':traceback.format_exc()})
    if rows:
        with (R/'native_confirmation.csv').open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0].to_dict())); w.writeheader(); w.writerows([r.to_dict() for r in rows])
    (R/'technical_failures.json').write_text(json.dumps(technical,indent=2),encoding='utf-8')
    return rows

