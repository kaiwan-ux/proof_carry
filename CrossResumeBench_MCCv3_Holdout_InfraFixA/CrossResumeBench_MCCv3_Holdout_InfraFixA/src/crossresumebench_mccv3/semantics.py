from __future__ import annotations
import copy,tempfile
from pathlib import Path
from .store import SemanticStore

def apply_plan(plan,store_path):
    s=SemanticStore(store_path)
    for a in plan: s.apply(a)
    return s.read()
def apply_source_pause(case,store_path): return apply_plan(case.source_plan,store_path)
def oracle_plan(case): return copy.deepcopy(case.oracle_plan)
def expected_source(case):
    with tempfile.TemporaryDirectory() as td: return apply_source_pause(case,Path(td)/'s.json')
def expected_final(case):
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/'s.json'; apply_source_pause(case,p); apply_plan(case.oracle_plan,p); return SemanticStore(p).read()

def _fact(ps,ft,sub,default=None): return ps.get(ft,sub,default)
def proof_plan(ps,case):
    p=case.params; f=case.family
    def one(kind,pp):
        a=[]
        if kind=='effect_commitment':
            st=_fact(ps,'effect_status',pp['operation']);
            if st=='not_committed': a.append({'kind':'effect','operation':pp['operation'],'unit':pp['effect_unit']})
            a += [{'kind':'unit','unit':pp['ack_unit']}]
        elif kind=='retry_pause':
            cur=int(_fact(ps,'retry_current',pp['retry_unit'])); mx=int(_fact(ps,'retry_bound',pp['retry_unit']))
            if cur<mx: a += [{'kind':'unit','unit':f"{pp['attempt_prefix']}{cur+1}"},{'kind':'counter','key':pp['counter_key'],'value':cur+1}]
            else: a.append({'kind':'unit','unit':pp['exhausted_unit']})
        elif kind=='approval_wait':
            st=_fact(ps,'approval_state',pp['request_id'])
            if st=='pending': a.append({'kind':'approval','id':pp['request_id'],'unit':pp['approval_unit']})
        elif kind=='parallel_join':
            for b in pp['branches']:
                if _fact(ps,'semantic_completion',b)!='completed': a.append({'kind':'unit','unit':b})
            a.append({'kind':'unit','unit':pp['join']})
        elif kind=='loop_pause':
            cur=int(_fact(ps,'counter_state',pp['counter_key'])); total=int(_fact(ps,'counter_bound',pp['counter_key'])); br=_fact(ps,'decision_state',pp['break_key'])
            br=(str(br).lower()=='true') if isinstance(br,str) else bool(br)
            if not br:
                for i in range(cur+1,total+1): a += [{'kind':'unit','unit':f"{pp['iter_prefix']}{i}"},{'kind':'counter','key':pp['counter_key'],'value':i}]
            a.append({'kind':'unit','unit':pp['exit_unit']})
        elif kind=='compensation_pending':
            est=_fact(ps,'effect_status',pp['operation']); cst=_fact(ps,'compensation_state',pp['compensation'])
            if est=='committed' and cst=='pending': a.append({'kind':'compensation','action':pp['compensation'],'unit':pp['comp_unit']})
            else: a.append({'kind':'unit','unit':pp['skip_unit']})
        elif kind=='async_callback':
            st=_fact(ps,'callback_state',pp['callback_id'])
            if st=='pending': a.append({'kind':'callback','id':pp['callback_id'],'unit':pp['callback_unit']})
        else: raise KeyError(kind)
        return a
    if f=='composite':
        plan=[]
        for c in p['components']: plan.extend(one(c['kind'],c['params']))
        return plan+[{'kind':'finish'}]
    return one(f,p)+[{'kind':'finish'}]
