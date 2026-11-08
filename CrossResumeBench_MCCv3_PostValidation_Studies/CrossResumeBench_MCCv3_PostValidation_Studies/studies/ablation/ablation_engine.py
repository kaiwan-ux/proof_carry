from __future__ import annotations
import copy, hashlib, json, sys
from pathlib import Path
from mechanism.mcc_v3 import build_mcc_v3, resolve_proofs, verify_certificate
from crossresumebench_mccv3.semantics import proof_plan
from crossresumebench_mccv3.models import NativePause

ROOT=Path(__file__).resolve().parents[2]; MECH=ROOT/'mechanism'
ABLATIONS=['full_mcc_v3','minus_closed_world_gate','minus_integrity_verification','minus_identity_binding','minus_complete_snapshots','history_only','certificates_only']

def _rehash_cert(c):
    x=copy.deepcopy(c)
    body={'fact_type':x['fact_type'],'subject':x['subject'],'value':x.get('value'),'scope':x['scope'],'evidence':x.get('evidence',{})}
    x['evidence_hash']=hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()
    return x

def transform_payload(payload,ablation):
    p=copy.deepcopy(payload)
    if ablation=='minus_integrity_verification':
        # Diagnostic: emulate accepting certificate contents without validating their hash.
        p['certificates']=[(_rehash_cert(c) if not verify_certificate(c) else c) for c in p.get('certificates',[])]
    elif ablation=='minus_identity_binding':
        p['certificates']=[c for c in p.get('certificates',[]) if c.get('fact_type')!='identity_binding']
    elif ablation=='minus_complete_snapshots':
        p['certificates']=[c for c in p.get('certificates',[]) if c.get('fact_type') not in {'completion_snapshot','obligation_snapshot'}]
    elif ablation=='history_only': p['certificates']=[]
    elif ablation=='certificates_only': p['history']=[]
    return p

def _get(ps,ft,sub,default=None): return ps.get(ft,sub,default)
def permissive_plan(ps,case):
    # Fixed missing-value defaults; deliberately NOT truth-aware. This diagnostic estimates
    # what happens when the closed-world rejection gate is removed.
    def one(kind,p):
        a=[]
        if kind=='effect_commitment':
            st=_get(ps,'effect_status',p['operation'],'committed')
            if st=='not_committed': a.append({'kind':'effect','operation':p['operation'],'unit':p['effect_unit']})
            a.append({'kind':'unit','unit':p['ack_unit']})
        elif kind=='retry_pause':
            cur=int(_get(ps,'retry_current',p['retry_unit'],0) or 0); mx=int(_get(ps,'retry_bound',p['retry_unit'],0) or 0)
            if cur<mx: a += [{'kind':'unit','unit':f"{p['attempt_prefix']}{cur+1}"},{'kind':'counter','key':p['counter_key'],'value':cur+1}]
            else: a.append({'kind':'unit','unit':p['exhausted_unit']})
        elif kind=='approval_wait':
            if _get(ps,'approval_state',p['request_id'],'absent')=='pending': a.append({'kind':'approval','id':p['request_id'],'unit':p['approval_unit']})
        elif kind=='parallel_join':
            for b in p['branches']:
                if _get(ps,'semantic_completion',b,'not_completed')!='completed': a.append({'kind':'unit','unit':b})
            a.append({'kind':'unit','unit':p['join']})
        elif kind=='loop_pause':
            cur=int(_get(ps,'counter_state',p['counter_key'],0) or 0); total=int(_get(ps,'counter_bound',p['counter_key'],0) or 0); br=_get(ps,'decision_state',p['break_key'],False); br=str(br).lower()=='true' if isinstance(br,str) else bool(br)
            if not br:
                for i in range(cur+1,total+1): a += [{'kind':'unit','unit':f"{p['iter_prefix']}{i}"},{'kind':'counter','key':p['counter_key'],'value':i}]
            a.append({'kind':'unit','unit':p['exit_unit']})
        elif kind=='compensation_pending':
            est=_get(ps,'effect_status',p['operation'],'unknown'); cst=_get(ps,'compensation_state',p['compensation'],'absent')
            a += ([{'kind':'compensation','action':p['compensation'],'unit':p['comp_unit']}] if est=='committed' and cst=='pending' else [{'kind':'unit','unit':p['skip_unit']}])
        elif kind=='async_callback':
            if _get(ps,'callback_state',p['callback_id'],'absent')=='pending': a.append({'kind':'callback','id':p['callback_id'],'unit':p['callback_unit']})
        return a
    out=[]
    if case.family=='composite':
        for c in case.params['components']: out.extend(one(c['kind'],c['params']))
    else: out.extend(one(case.family,case.params))
    return out+[{'kind':'finish'}]

def resolve_ablation(payload,case,ablation):
    p=transform_payload(payload,ablation)
    ps,rep=resolve_proofs(p,case.continuation_contract,MECH)
    if rep['admissible']: return p,proof_plan(ps,case),'',rep
    if ablation=='minus_closed_world_gate':
        types={x.get('type') for x in rep.get('unresolved',[])}
        if types and types <= {'UNPROVEN_REQUIRED_FACT'}:
            return p,permissive_plan(ps,case),'',{'admissible':True,'diagnostic_override':'closed_world_gate_removed','original_report':rep}
    return p,None,rep.get('reason','REJECTED'),rep
