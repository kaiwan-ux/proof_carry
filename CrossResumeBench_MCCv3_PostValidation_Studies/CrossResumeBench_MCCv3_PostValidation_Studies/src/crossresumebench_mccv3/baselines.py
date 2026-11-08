from __future__ import annotations
import hashlib,json,copy,sys
from pathlib import Path
from .legacy import to_source_capture,v2_case_spec
from .evidence import legacy_capture
from .semantics import proof_plan
ROOT=Path(__file__).resolve().parents[2]; FROZEN=ROOT/'frozen_v2'; MECH=ROOT/'mechanism'
if str(FROZEN/'src') not in sys.path: sys.path.insert(0,str(FROZEN/'src'))
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from crossresumebench_v2.mcc import build_mcc_v2,reconstruct_mcc_v2,admissibility
from crossresumebench_v2.models import ReconstructedContinuation
from mechanism.mcc_v3 import build_mcc_v3,resolve_proofs
METHODS=['mcc_v3','mcc_v2_frozen','history_inference','aaif_reference','caplease_reference','aaif_plus_caplease_reference','explicit_minimal','oracle']

def _workflow_hash(v2c): return hashlib.sha256(json.dumps({'target_actions':v2c.target_actions,'dependencies':v2c.target_dependencies},sort_keys=True,separators=(',',':')).encode()).hexdigest()
def _legacy_rc_from_history(cap,case):
    rc=ReconstructedContinuation(cap.case_id,cap.workflow,dict(cap.app_state))
    for e in cap.portable_history:
        t=e.get('type');u=e.get('semantic_unit');d=e.get('data',{})
        if t=='semantic_unit_completed' and u: rc.completed_units.append(u)
        elif t=='tool_call_observed' and d.get('commit_status') in {'committed','not_committed'}: rc.effect_facts[d.get('operation')]={'status':d.get('commit_status'),'source':'history'}
        elif t=='approval_requested': rc.pending_obligations.append({'type':'approval','id':d.get('request_id'),'blocks':d.get('blocks')})
        elif t=='callback_pending': rc.pending_obligations.append({'type':'callback','id':d.get('callback_id'),'operation':d.get('operation')})
        elif t=='compensation_required': rc.pending_obligations.append({'type':'compensation','action':d.get('compensation_action'),'effect':d.get('effect')})
        elif t=='counter_observed': rc.counters[str(d.get('key'))]=int(d.get('value',0))
        elif t=='decision_made': rc.decisions[str(d.get('key'))]=d.get('choice')
        elif t=='retry_failed':
            rc.counters[f'retry:{u}']=int(d.get('attempt',0)); rc.pending_obligations.append({'type':'retry','step':u,'next_attempt':int(d.get('attempt',0))+1,'max_attempts':int(d.get('max_attempts',0))})
        elif t=='join_observed' and u: rc.dependencies[u]=list(d.get('requires',[]))
    return rc

def legacy_plan(rc,case):
    # Reproduces MCC v2's permissive missing-as-default behavior for comparison.
    def one(kind,p):
        a=[]
        if kind=='effect_commitment':
            if rc.effect_facts.get(p['operation'],{}).get('status','unknown')=='not_committed': a.append({'kind':'effect','operation':p['operation'],'unit':p['effect_unit']})
            a.append({'kind':'unit','unit':p['ack_unit']})
        elif kind=='retry_pause':
            obs=next((o for o in rc.pending_obligations if o.get('type')=='retry' and o.get('step') in {p['retry_unit'],'src_alias__'+p['retry_unit']}),None)
            if obs:
                nxt=int(obs.get('next_attempt',1)); mx=int(obs.get('max_attempts',0)); a += ([{'kind':'unit','unit':f"{p['attempt_prefix']}{nxt}"},{'kind':'counter','key':p['counter_key'],'value':nxt}] if nxt<=mx and mx>0 else [{'kind':'unit','unit':p['exhausted_unit']}])
            else: a += [{'kind':'unit','unit':f"{p['attempt_prefix']}1"},{'kind':'counter','key':p['counter_key'],'value':1}]
        elif kind=='approval_wait':
            if any(o.get('type')=='approval' and o.get('id')==p['request_id'] for o in rc.pending_obligations): a.append({'kind':'approval','id':p['request_id'],'unit':p['approval_unit']})
        elif kind=='parallel_join':
            done=set(rc.completed_units)
            for b in p['branches']:
                if b not in done: a.append({'kind':'unit','unit':b})
            a.append({'kind':'unit','unit':p['join']})
        elif kind=='loop_pause':
            cur=int(rc.counters.get(p['counter_key'],0)); br=rc.decisions.get(p['break_key'],False)
            if not br:
                for i in range(cur+1,p['total']+1): a += [{'kind':'unit','unit':f"{p['iter_prefix']}{i}"},{'kind':'counter','key':p['counter_key'],'value':i}]
            a.append({'kind':'unit','unit':p['exit_unit']})
        elif kind=='compensation_pending':
            est=rc.effect_facts.get(p['operation'],{}).get('status','unknown'); pending=any(o.get('type')=='compensation' and o.get('action')==p['compensation'] for o in rc.pending_obligations)
            a += ([{'kind':'compensation','action':p['compensation'],'unit':p['comp_unit']}] if est=='committed' and pending else [{'kind':'unit','unit':p['skip_unit']}])
        elif kind=='async_callback':
            if any(o.get('type')=='callback' and o.get('id')==p['callback_id'] for o in rc.pending_obligations): a.append({'kind':'callback','id':p['callback_id'],'unit':p['callback_unit']})
        return a
    plan=[]
    if case.family=='composite':
        for c in case.params['components']: plan.extend(one(c['kind'],c['params']))
    else: plan=one(case.family,case.params)
    return plan+[{'kind':'finish'}]

def build_and_lower(method,capture,case,target):
    v2c=v2_case_spec(case); wh=_workflow_hash(v2c)
    if method=='mcc_v3':
        payload=build_mcc_v3(capture,target,wh,case.continuation_contract,MECH); ps,rep=resolve_proofs(payload,case.continuation_contract,MECH)
        if not rep['admissible']: return payload,None,rep['reason'],rep
        return payload,proof_plan(ps,case),'',rep
    lc=legacy_capture(capture); sc=to_source_capture(lc)
    if method=='mcc_v2_frozen':
        pkg=build_mcc_v2(sc,target,wh,FROZEN); rc,rep=reconstruct_mcc_v2(pkg.payload,v2c,FROZEN); ok,reason=admissibility(rc)
        return pkg.payload,(legacy_plan(rc,case) if ok else None),(reason or ''),rep
    if method=='history_inference':
        rc=_legacy_rc_from_history(sc,case); return {'app_state':sc.app_state,'history':sc.portable_history},legacy_plan(rc,case),'',{}
    if method in {'aaif_reference','caplease_reference','aaif_plus_caplease_reference'}:
        rc=_legacy_rc_from_history(sc,case)
        if method!='aaif_reference':
            for c in sc.certificates:
                if c.get('fact_type')=='effect_commitment': rc.effect_facts[c['subject']]={'status':c.get('value'),'source':'reference'}
        if method=='aaif_reference' and any(e.get('type')=='tool_call_observed' and e.get('data',{}).get('commit_status')=='unknown' for e in sc.portable_history): return {'method':method},None,'AAIF_REFERENCE_AMBIGUOUS_EFFECT',{}
        return {'method':method,'history':sc.portable_history},legacy_plan(rc,case),'',{}
    if method in {'explicit_minimal','oracle'}: return {'method':method,'privileged':True},copy.deepcopy(case.oracle_plan),'',{}
    raise KeyError(method)
