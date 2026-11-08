from __future__ import annotations
from copy import deepcopy
from typing import Any
import json

# Generic, workflow-name-independent normalization + reconstruction.
def _canon(e): return (e.get('kind'),e.get('step'),json.dumps(e.get('detail',{}),sort_keys=True,default=str))
def normalize_history(trace:list[dict[str,Any]])->list[dict[str,Any]]:
    ordered=sorted(deepcopy(trace),key=lambda e:int(e.get('seq',10**9)))
    out=[]; seen=set()
    for e in ordered:
        if e.get('kind')=='observation_noise': continue
        key=_canon(e)
        if key in seen: continue
        seen.add(key); out.append(e)
    return out

def portable_history(trace): return deepcopy(trace)

def _materialize(v,sem):
    if not isinstance(v,str) or not v.startswith('$'): return deepcopy(v)
    if v.startswith('$decision:'): return sem['decisions'].get(v.split(':',1)[1])
    if v.startswith('$loop_next:'): return sem['loop_counters'].get(v.split(':',1)[1],0)+1
    return v

def _match(cond,sem):
    if not cond:return True
    if 'obligation_type' in cond and not any(x.get('type')==cond['obligation_type'] for x in sem['pending_obligations']):return False
    for step,n in (cond.get('retry_at_least') or {}).items():
        if sem['retry_counts'].get(step,0)<int(n):return False
    for k,val in (cond.get('decision') or {}).items():
        if sem['decisions'].get(k)!=val:return False
    for step in cond.get('completed_all',[]):
        if step not in sem['completed']:return False
    return True

def infer_semantics(workflow,history,static_spec):
    history=normalize_history(history)
    completed=[]; retry_counts={}; decisions={}; loops={}; receipts={}; ambiguities=[]; inferred=[]; open_by_id={}
    for e in history:
        k=e.get('kind'); step=e.get('step'); d=e.get('detail',{})
        if k=='step_completed': completed.append(step)
        elif k in {'retry_failed','retry_succeeded'}: retry_counts[step]=max(retry_counts.get(step,0),int(d.get('attempt',1)))
        elif k=='decision_made': decisions[str(d.get('key','decision'))]=d.get('choice')
        elif k=='loop_iteration_completed': loops[str(d.get('loop_id',step))]=max(loops.get(str(d.get('loop_id',step)),0),int(d.get('iteration',0)))
        elif k=='obligation_opened':
            detail={kk:vv for kk,vv in d.items() if kk!='id'}
            if 'obligation_step' in detail: detail['step']=detail.pop('obligation_step')
            open_by_id[str(d.get('id'))]={"type":step,"id":d.get('id'),**detail}
        elif k=='obligation_resolved': open_by_id.pop(str(d.get('id')),None)
        elif k=='effect_commit_ack': receipts[step]={"operation_id":d.get('operation_id'),"status":d.get('status','committed'),"replay":d.get('replay','forbidden'),"inferred_from":"effect_commit_ack"}
        elif k=='tool_call_observed' and d.get('commit_status')=='unknown': ambiguities.append({'type':'effect_commit_unknown','operation':step})
    obligations=list(open_by_id.values())
    sem={'completed':completed,'retry_counts':retry_counts,'decisions':decisions,'loop_counters':loops,'pending_obligations':obligations,'effect_receipts':receipts,'control_frontier':{},'continuation_contract':deepcopy(static_spec.get('contract',{}))}
    for field in ['completed','retry_counts','decisions','loop_counters','pending_obligations','effect_receipts','continuation_contract']:
        if sem[field]:inferred.append(field)
    for rule in static_spec.get('frontier_rules',[]):
        if _match(rule.get('when',{}),sem): sem['control_frontier']={k:_materialize(v,sem) for k,v in rule.get('frontier',{}).items()}; break
    if sem['control_frontier']:inferred.append('control_frontier')
    return sem,{'ambiguities':ambiguities,'inferred_fields':sorted(set(inferred)),'static_spec_used':True,'generic_engine':True,'normalized_events':len(history)}

def apply_inferred(state,inferred,only_missing=True):
    s=state.clone()
    for attr in ['completed','retry_counts','decisions','loop_counters','control_frontier','pending_obligations','effect_receipts','continuation_contract']:
        val=deepcopy(inferred.get(attr)); cur=getattr(s,attr); empty=cur in ({},[],None,0,'')
        if val and (not only_missing or empty):setattr(s,attr,val)
    return s
