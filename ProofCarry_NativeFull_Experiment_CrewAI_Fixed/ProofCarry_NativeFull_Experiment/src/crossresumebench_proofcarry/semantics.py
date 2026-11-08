from __future__ import annotations
import tempfile
from pathlib import Path
from .store import SemanticStore

def apply_plan(plan,store_path):
    s=SemanticStore(store_path)
    for a in plan: s.apply(a)
    return s.read()
def apply_source_pause(case,store_path): return apply_plan(case.source_plan,store_path)
def oracle_plan(case): return list(case.oracle_plan)+[{'kind':'finish'}]
def expected_source(case):
    with tempfile.TemporaryDirectory() as td: return apply_source_pause(case,Path(td)/'s.json')
def expected_final(case):
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/'s.json'; apply_source_pause(case,p); apply_plan(oracle_plan(case),p); return SemanticStore(p).read()

def _get(ps,ft,sub): return ps.get(ft,sub,None)
def proof_plan(ps,case,allow_defaults=False):
    p=case.params; fam=case.family
    def one(kind,x):
        a=[]
        if kind=='effect_commitment':
            st=_get(ps,'effect_status',x['operation'])
            if st is None and allow_defaults: st='not_committed'
            if st=='not_committed': a.append({'kind':'effect','operation':x['operation'],'unit':x['effect_unit']})
            elif st=='partial': a += [{'kind':'compensation','action':x['partial_compensation'],'unit':x['partial_comp_unit']},{'kind':'effect','operation':x['operation'],'unit':x['effect_unit']}]
            elif st!='committed': return None
            a.append({'kind':'unit','unit':x['ack_unit']})
        elif kind=='retry':
            cur=_get(ps,'retry_current',x['retry_unit']); mx=_get(ps,'retry_bound',x['retry_unit'])
            if allow_defaults: cur=0 if cur is None else cur; mx=x['max_attempts'] if mx is None else mx
            if cur is None or mx is None: return None
            cur,mx=int(cur),int(mx)
            if cur<mx: a += [{'kind':'unit','unit':f"{x['attempt_prefix']}{cur+1}"},{'kind':'counter','key':x['counter_key'],'value':cur+1}]
            else: a.append({'kind':'unit','unit':x['exhausted_unit']})
        elif kind=='approval':
            st=_get(ps,'approval_state',x['request_id'])
            if st is None and allow_defaults: st='granted'
            if st=='pending': a.append({'kind':'approval','id':x['request_id'],'unit':x['approval_unit']})
            elif st=='granted': a.append({'kind':'unit','unit':x['proceed_unit']})
            elif st=='expired': a.append({'kind':'approval','id':x['renew_id'],'unit':x['renew_unit']})
            elif st=='revoked': a.append({'kind':'unit','unit':x['abort_unit']})
            else: return None
        elif kind=='parallel':
            for b in x['branches']:
                st=_get(ps,'branch_state',b)
                if st is None and allow_defaults: st='pending'
                if st=='pending': a.append({'kind':'unit','unit':b})
                elif st=='failed': a += [{'kind':'unit','unit':f'{b}_recover'},{'kind':'unit','unit':b}]
                elif st!='completed': return None
            a.append({'kind':'unit','unit':x['join']})
        elif kind=='loop':
            cur=_get(ps,'loop_current',x['counter_key']); total=_get(ps,'loop_bound',x['counter_key']); br=_get(ps,'decision_state',x['break_key'])
            if allow_defaults: cur=0 if cur is None else cur; total=x['total'] if total is None else total; br=False if br is None else br
            if cur is None or total is None or br is None: return None
            cur,total=int(cur),int(total); br=bool(br)
            if not br:
                for i in range(cur+1,total+1): a += [{'kind':'unit','unit':f"{x['iter_prefix']}{i}"},{'kind':'counter','key':x['counter_key'],'value':i}]
            a.append({'kind':'unit','unit':x['exit_unit']})
        elif kind=='compensation':
            est=_get(ps,'effect_status',x['operation']); cst=_get(ps,'compensation_state',x['compensation'])
            if allow_defaults: est='not_committed' if est is None else est; cst='absent' if cst is None else cst
            if est is None or cst is None: return None
            if est=='committed' and cst=='pending': a.append({'kind':'compensation','action':x['compensation'],'unit':x['comp_unit']})
            elif est=='committed' and cst=='completed': a.append({'kind':'unit','unit':x['completed_unit']})
            elif est=='not_committed': a.append({'kind':'unit','unit':x['skip_unit']})
            else: return None
        elif kind=='callback':
            st=_get(ps,'callback_state',x['callback_id'])
            if st is None and allow_defaults: st='received'
            if st=='pending': a.append({'kind':'callback','id':x['callback_id'],'unit':x['callback_unit']})
            elif st=='received': a.append({'kind':'unit','unit':x['process_unit']})
            elif st=='expired': a.append({'kind':'unit','unit':x['expired_unit']})
            elif st=='wrong_execution': a += [{'kind':'unit','unit':x['wrong_unit']},{'kind':'unit','unit':x['expired_unit']}]
            else: return None
        return a
    plan=[]
    if fam=='composite':
        for c in p['components']:
            z=one(c['kind'],c['params'])
            if z is None: return None
            plan.extend(z)
    else:
        z=one(fam,p)
        if z is None: return None
        plan=z
    return plan+[{'kind':'finish'}]
