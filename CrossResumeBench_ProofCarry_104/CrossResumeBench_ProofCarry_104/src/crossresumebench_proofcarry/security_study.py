from __future__ import annotations
import copy,hashlib,json,time,traceback
from .cases import CASES
from .runner import PAIRS,fake_native,write_csv
from .evidence import generate,target_contract,workflow_hash,VERIFICATION_TIME
from .baselines import PUBLIC_KEYS
from mechanism.proofcarry import build_payload,resolve,contract_hash
from mechanism.crypto import ReplayCache,deterministic_test_private_key,sign_body

METHODS=['proofcarry','unkeyed_hash_control']
ATTACKS=[
    'valid_control',
    'replay_execution',
    'forgery_value',
    'hash_recompute_forgery',
    'contract_substitution',
    'runtime_substitution',
    'expired_certificate',
    'nonce_reuse',
    'unauthorized_identity_binding',
]

def _signed_payload(case,source,target):
    cap=generate(case,fake_native(case,source),source,target,'enough_evidence')
    con=target_contract(case,target)
    return con,build_payload(cap,target,workflow_hash(case),con)

def _old_hash(ft,sub,val,scope,evidence):
    body={'fact_type':ft,'subject':sub,'value':val,'scope':scope,'evidence':evidence}
    return hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()

def _plain_payload(case,source,target,signed):
    certs=[]
    for c in signed['certificates']:
        d={'certificate_id':c['certificate_id'],'fact_type':c['fact_type'],'subject':c['subject'],'value':copy.deepcopy(c.get('value')),'scope':case.case_id,'evidence':copy.deepcopy(c.get('evidence',{}))}
        d['evidence_hash']=_old_hash(d['fact_type'],d['subject'],d.get('value'),d['scope'],d['evidence'])
        certs.append(d)
    return {
        'case_id':case.case_id,
        'execution_id':signed['execution_id'],  # carried for attack simulation but not authenticated by the old-style verifier
        'source_runtime':source,
        'target_runtime':target,
        'workflow_spec_hash':signed['workflow_spec_hash'],
        'continuation_contract_hash':signed['continuation_contract_hash'],
        'certificates':certs,
    }

def _plain_accepts(payload,contract):
    if payload.get('continuation_contract_hash')!=contract_hash(contract):
        return False,'CONTRACT_HASH_MISMATCH'
    for c in payload.get('certificates',[]):
        expected=_old_hash(c['fact_type'],c['subject'],c.get('value'),c['scope'],c.get('evidence',{}))
        if c.get('evidence_hash')!=expected:
            return False,'INVALID_INTEGRITY_HASH'
    # Deliberately no issuer authentication, execution/runtime binding, expiry,
    # nonce/replay protection, or approved semantic-binding check.
    return True,''

def _attack_proofcarry(p,con,attack,source):
    p=copy.deepcopy(p); con2=copy.deepcopy(con); cache=ReplayCache()
    if attack=='replay_execution':
        p['execution_id']=p['execution_id']+'::other'
    elif attack in {'forgery_value','hash_recompute_forgery'}:
        c=p['certificates'][0]; c['value']='FORGED_VALUE'  # no private-key re-signing
    elif attack=='contract_substitution':
        con2['version']='substituted'; p['continuation_contract_hash']='0'*64
    elif attack=='runtime_substitution':
        p['target_runtime']=source
    elif attack=='expired_certificate':
        c=p['certificates'][0]; c['expires_at']=VERIFICATION_TIME-1
        body={k:v for k,v in c.items() if k!='signature'}; c['signature']=sign_body(body,deterministic_test_private_key())
    elif attack=='nonce_reuse':
        c=p['certificates'][0]; cache.mark(c['issuer_id'],c['nonce'])
    elif attack=='unauthorized_identity_binding':
        c=next(x for x in p['certificates'] if x.get('fact_type')=='identity_binding'); c['value']='canonical::wrong_subject'
        body={k:v for k,v in c.items() if k!='signature'}; c['signature']=sign_body(body,deterministic_test_private_key())
    return p,con2,cache

def _attack_plain(p,con,attack,source):
    p=copy.deepcopy(p); con2=copy.deepcopy(con)
    if attack=='replay_execution':
        p['execution_id']=p['execution_id']+'::other'  # verifier does not bind this field
    elif attack=='forgery_value':
        p['certificates'][0]['value']='FORGED_VALUE'  # stale hash -> reject
    elif attack=='hash_recompute_forgery':
        c=p['certificates'][0]; c['value']='FORGED_VALUE'; c['evidence_hash']=_old_hash(c['fact_type'],c['subject'],c.get('value'),c['scope'],c.get('evidence',{}))
    elif attack=='contract_substitution':
        con2['version']='substituted'; p['continuation_contract_hash']='0'*64
    elif attack=='runtime_substitution':
        p['target_runtime']=source  # certificate has no runtime binding
    elif attack=='expired_certificate':
        pass  # old-style certificate has no authenticated expiration
    elif attack=='nonce_reuse':
        pass  # old-style certificate has no nonce/replay state
    elif attack=='unauthorized_identity_binding':
        c=next(x for x in p['certificates'] if x.get('fact_type')=='identity_binding'); c['value']='canonical::wrong_subject'; c['evidence_hash']=_old_hash(c['fact_type'],c['subject'],c.get('value'),c['scope'],c.get('evidence',{}))
    return p,con2

def run(results):
    from pathlib import Path
    rows=[]; results=Path(results)
    for case in CASES:
      for source,target in PAIRS:
        con,signed=_signed_payload(case,source,target)
        plain=_plain_payload(case,source,target,signed)
        for attack in ATTACKS:
          expected='safe_completion' if attack=='valid_control' else 'safe_rejection'
          for method in METHODS:
            t0=time.perf_counter_ns()
            try:
                if method=='proofcarry':
                    p,con2,cache=_attack_proofcarry(signed,con,attack,source)
                    _,rep=resolve(p,con2,PUBLIC_KEYS,VERIFICATION_TIME,cache)
                    accepted=bool(rep['admissible']); reason=rep.get('reason','')
                else:
                    p,con2=_attack_plain(plain,con,attack,source)
                    accepted,reason=_plain_accepts(p,con2)
                outcome='safe_completion' if accepted else 'safe_rejection'
                unsafe=int(outcome!=expected)
                rows.append({'method':method,'case_id':case.case_id,'family':case.family,'source':source,'target':target,'attack':attack,'expected':expected,'outcome':outcome,'unsafe':unsafe,'technical_failure':0,'reject_reason':reason,'latency_ms':(time.perf_counter_ns()-t0)/1e6})
            except Exception:
                rows.append({'method':method,'case_id':case.case_id,'family':case.family,'source':source,'target':target,'attack':attack,'expected':expected,'outcome':'technical','unsafe':0,'technical_failure':1,'error':traceback.format_exc()})
    write_csv(results/'security_runs.csv',rows); return rows
