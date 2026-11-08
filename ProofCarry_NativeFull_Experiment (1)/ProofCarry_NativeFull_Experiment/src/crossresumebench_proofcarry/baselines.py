from __future__ import annotations
import copy,hashlib,json,sys
from pathlib import Path
from mechanism.crypto import public_key_b64,ReplayCache
from mechanism.proofcarry import build_payload,resolve
from .evidence import workflow_hash,target_contract,ISSUER,VERIFICATION_TIME
from .semantics import proof_plan
ROOT=Path(__file__).resolve().parents[2]
PLAIN=ROOT/'frozen_mccv3_plain'; FROZEN_V2=ROOT/'frozen_v2'
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
if str(FROZEN_V2/'src') not in sys.path: sys.path.insert(0,str(FROZEN_V2/'src'))
from frozen_mccv3_plain.mcc_v3 import build_mcc_v3 as plain_build, resolve_proofs as plain_resolve
PUBLIC_KEYS={ISSUER:public_key_b64()}
METHODS=['proofcarry','proofcarry_no_auth','legacy_permissive','history_only','always_reject','aaif_reference','caplease_reference','aaif_plus_caplease_reference','explicit_minimal','oracle']

def _proofcarry(capture,case,target,options=None):
    con=target_contract(case,target); p=build_payload(capture,target,workflow_hash(case),con); ps,rep=resolve(p,con,PUBLIC_KEYS,VERIFICATION_TIME,ReplayCache(),options=options)
    if not rep['admissible']: return p,None,rep['reason'],rep
    plan=proof_plan(ps,case,allow_defaults=bool(options and not options.get('closed_world',True)))
    if plan is None: return p,None,'NO_PLAN_FROM_PROOFS',rep
    return p,plan,'',rep

def _history_state(capture,case,allow_defaults=True):
    class P:
        def __init__(self): self.d={}
        def get(self,ft,sub,default=None): return self.d.get(f'{ft}|{sub}',default)
    ps=P()
    # naive runtime-prefix stripping intentionally represents permissive semantic guessing.
    def canon(s): return str(s).split('::',1)[-1]
    for e in capture.get('history',[]):
        if e.get('type')=='fact_observed': ps.d[f"{e['fact_type']}|{canon(e['subject'])}"]=e.get('value')
        elif e.get('type')=='retry_observed':
            sub=canon(e['subject']); ps.d[f'retry_current|{sub}']=e['data'].get('current')
            if 'bound' in e['data']: ps.d[f'retry_bound|{sub}']=e['data'].get('bound')
        elif e.get('type')=='loop_observed': ps.d[f"loop_current|{canon(e['subject'])}"]=e['data'].get('current')
    return ps

def _plain_capture(capture,case,source,target):
    # Convert signed certs into old SHA256 trusted-witness format so frozen MCC v3 can be compared on semantic safety, not authentication.
    import hashlib
    con=target_contract(case,target); cs=[]
    def h(ft,sub,val,scope,evidence): return hashlib.sha256(json.dumps({'fact_type':ft,'subject':sub,'value':val,'scope':scope,'evidence':evidence},sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()
    for c in capture.get('certificates',[]):
        ft=c.get('fact_type'); sub=c.get('subject'); val=c.get('value'); ev=c.get('evidence',{}); scope=case.case_id
        mapped_ft=ft
        if ft=='fact_snapshot': mapped_ft='completion_snapshot' if isinstance(val,dict) and val.get('fact_type')=='semantic_completion' else 'fact_value'
        d={'certificate_id':c.get('certificate_id'),'case_id':case.case_id,'fact_type':mapped_ft,'subject':sub,'value':val,'scope':scope,'evidence':ev}; d['evidence_hash']=h(mapped_ft,sub,val,scope,ev); cs.append(d)
    return {'case_id':case.case_id,'workflow':capture['workflow'],'app_state':copy.deepcopy(capture['app_state']),'history':copy.deepcopy(capture['history']),'certificates':cs,'native_observation':{'framework':source}}

def build_and_lower(method,capture,case,target):
    if method=='proofcarry': return _proofcarry(capture,case,target)
    if method=='always_reject': return {'method':'always_reject'},None,'ALWAYS_REJECT',{}
    if method in {'oracle','explicit_minimal'}: return {'method':method,'privileged':True},copy.deepcopy(case.oracle_plan)+[{'kind':'finish'}],'',{}
    if method in {'history_only','legacy_permissive','aaif_reference','caplease_reference','aaif_plus_caplease_reference'}:
        ps=_history_state(capture,case); plan=proof_plan(ps,case,allow_defaults=True)
        if method=='aaif_reference' and any(f['fact_type']=='effect_status' for f in case.truth_facts): return {'method':method},None,'AAIF_REFERENCE_AMBIGUOUS_EFFECT',{}
        # CapLease-inspired references can recover effect status only, not all continuation obligations.
        if method in {'caplease_reference','aaif_plus_caplease_reference'}:
            for c in capture.get('certificates',[]):
                if c.get('fact_type')=='effect_status': ps.d[f"effect_status|{str(c['subject']).split('::',1)[-1]}"]=c.get('value')
            plan=proof_plan(ps,case,allow_defaults=True)
        return {'method':method,'history':capture.get('history',[])},plan,'',{}
    if method=='proofcarry_no_auth':
        # Frozen v3 plain cannot consume our richer multistate snapshot directly; use proofcarry resolver with signature verification disabled
        # but keep closed-world/binding/snapshot logic to isolate authentication/context-binding as the difference.
        return _proofcarry(capture,case,target,options={'verify_signatures':False,'use_identity_bindings':True,'use_snapshots':True,'closed_world':True})
    raise KeyError(method)

ABLATIONS={
 'full':{},
 'minus_closed_world_gate':{'closed_world':False},
 'minus_signature_verification':{'verify_signatures':False},
 'minus_identity_binding':{'use_identity_bindings':False},
 'minus_complete_snapshots':{'use_snapshots':False},
 'history_only':None,
 'certificates_only':'certificates_only',
}
def run_ablation(name,capture,case,target):
    if name=='history_only':
        x=copy.deepcopy(capture); x['certificates']=[]; return _proofcarry(x,case,target)
    if name=='certificates_only':
        x=copy.deepcopy(capture); x['history']=[]; return _proofcarry(x,case,target)
    opts={'verify_signatures':True,'use_identity_bindings':True,'use_snapshots':True,'closed_world':True}; opts.update(ABLATIONS[name]); return _proofcarry(capture,case,target,opts)
