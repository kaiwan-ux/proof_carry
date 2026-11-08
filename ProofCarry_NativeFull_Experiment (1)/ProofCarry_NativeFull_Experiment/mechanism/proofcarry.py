from __future__ import annotations
import copy,hashlib,json
from dataclasses import dataclass,field
from .crypto import verify_body,ReplayCache

def contract_hash(contract): return hashlib.sha256(json.dumps(contract,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()
@dataclass
class ProofState:
    facts:dict=field(default_factory=dict); provenance:dict=field(default_factory=dict); bindings:dict=field(default_factory=dict); unresolved:list=field(default_factory=list); invalid:list=field(default_factory=list)
    def get(self,ft,sub,default=None): return self.facts.get(f'{ft}|{sub}',default)

def build_payload(capture,target_runtime,workflow_spec_hash,contract):
    return {'proofcarry_version':'1.0','case_id':capture['case_id'],'execution_id':capture['execution_id'],'workflow':capture['workflow'],'source_runtime':capture['source_runtime'],'target_runtime':target_runtime,'workflow_spec_hash':workflow_spec_hash,'continuation_contract_hash':contract_hash(contract),'app_state':copy.deepcopy(capture['app_state']),'history':copy.deepcopy(capture['history']),'certificates':copy.deepcopy(capture['certificates'])}

def _body(cert): return {k:v for k,v in cert.items() if k!='signature'}
def _canon(sub,bindings):
    seen=set(); cur=str(sub)
    while cur in bindings and cur not in seen: seen.add(cur); cur=bindings[cur]
    return cur

def verify_certificate(cert,payload,contract,public_keys,verification_time,replay_cache=None,mark_nonce=True):
    issuer=cert.get('issuer_id'); pub=public_keys.get(issuer)
    if not pub: return False,'UNKNOWN_ISSUER'
    if cert.get('signature_alg')!='Ed25519' or not verify_body(_body(cert),cert.get('signature',''),pub): return False,'INVALID_SIGNATURE'
    checks={'execution_id':payload['execution_id'],'case_id':payload['case_id'],'workflow_spec_hash':payload['workflow_spec_hash'],'contract_hash':payload['continuation_contract_hash'],'source_runtime':payload['source_runtime'],'target_runtime':payload['target_runtime']}
    for k,v in checks.items():
        if cert.get(k)!=v: return False,f'CONTEXT_MISMATCH_{k.upper()}'
    now=int(verification_time)
    if not (int(cert.get('issued_at',0))<=now<=int(cert.get('expires_at',0))): return False,'CERTIFICATE_EXPIRED_OR_NOT_YET_VALID'
    nonce=str(cert.get('nonce',''))
    if not nonce: return False,'MISSING_NONCE'
    if replay_cache is not None and replay_cache.seen(issuer,nonce): return False,'NONCE_REUSE'
    if mark_nonce and replay_cache is not None: replay_cache.mark(issuer,nonce)
    return True,''

def resolve(payload,contract,public_keys,verification_time,replay_cache=None,options=None):
    options=options or {}; verify_signatures=options.get('verify_signatures',True); use_bindings=options.get('use_identity_bindings',True); use_snapshots=options.get('use_snapshots',True); closed_world=options.get('closed_world',True)
    ps=ProofState()
    if payload.get('continuation_contract_hash')!=contract_hash(contract): ps.unresolved.append({'type':'CONTRACT_HASH_MISMATCH'}); return ps,{'admissible':False,'reason':'CONTRACT_HASH_MISMATCH'}
    valid=[]
    local_cache=replay_cache or ReplayCache()
    for c in payload.get('certificates',[]):
        if verify_signatures:
            ok,reason=verify_certificate(c,payload,contract,public_keys,verification_time,local_cache)
            if not ok: ps.invalid.append({'id':c.get('certificate_id'),'reason':reason}); continue
        valid.append(c)
    if ps.invalid: ps.unresolved.append({'type':'INVALID_ATTESTATION','details':copy.deepcopy(ps.invalid)})
    allowed=contract.get('allowed_bindings',{})
    if use_bindings:
        for c in valid:
            if c.get('fact_type')!='identity_binding': continue
            sub,val=str(c.get('subject')),str(c.get('value'))
            if sub not in allowed or allowed[sub]!=val:
                ps.unresolved.append({'type':'UNAPPROVED_IDENTITY_BINDING','subject':sub,'value':val}); continue
            if sub in ps.bindings and ps.bindings[sub]!=val: ps.unresolved.append({'type':'CONFLICTING_IDENTITY_BINDING','subject':sub})
            else: ps.bindings[sub]=val
    raw=[]; snapshots=[]
    for e in payload.get('history',[]):
        t=e.get('type'); d=e.get('data',{}); sub=e.get('subject')
        if t=='fact_observed' and sub is not None: raw.append((e['fact_type'],sub,e.get('value'),'history'))
        elif t=='retry_observed':
            raw += [('retry_current',e['subject'],int(d['current']),'history')]
            if 'bound' in d: raw += [('retry_bound',e['subject'],int(d['bound']),'history')]
        elif t=='loop_observed': raw.append(('loop_current',e['subject'],int(d['current']),'history'))
    for c in valid:
        ft,sub,val=c.get('fact_type'),str(c.get('subject')),c.get('value')
        if ft=='identity_binding': continue
        if ft=='fact_snapshot': snapshots.append(c); continue
        raw.append((ft,sub,val,'certificate'))
    def add(ft,sub,val,prov):
        sub=_canon(sub,ps.bindings) if use_bindings else str(sub); k=f'{ft}|{sub}'
        if k in ps.facts and ps.facts[k]!=val: ps.unresolved.append({'type':'CONFLICTING_FACT','fact_type':ft,'subject':sub})
        else: ps.facts[k]=copy.deepcopy(val); ps.provenance.setdefault(k,[]).append(prov)
    for ft,sub,val,prov in raw: add(ft,sub,val,prov)
    if use_snapshots:
        for c in snapshots:
            val=c.get('value',{})
            if not isinstance(val,dict) or not val.get('complete'): continue
            ft=str(val.get('fact_type')); states=val.get('states',{})
            for sub,state in states.items(): add(ft,sub,state,'certificate:complete_snapshot')
    # Requirements use target-runtime aliases and become canonical only through verified bindings.
    for r in contract.get('required_facts',[]):
        sub=_canon(r['subject'],ps.bindings) if use_bindings else str(r['subject']); k=f"{r['fact_type']}|{sub}"
        if k not in ps.facts and closed_world: ps.unresolved.append({'type':'UNPROVEN_REQUIRED_FACT','fact_type':r['fact_type'],'subject':sub,'purpose':r.get('purpose','')})
    ok=not ps.unresolved
    return ps,{'admissible':ok,'reason':'' if ok else ';'.join(sorted({x['type'] for x in ps.unresolved})),'unresolved':copy.deepcopy(ps.unresolved),'provenance':copy.deepcopy(ps.provenance),'bindings':dict(ps.bindings)}
