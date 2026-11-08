from __future__ import annotations
import copy, hashlib, json
from pathlib import Path
from jsonschema import Draft202012Validator
from .proofs import ProofState, contract_hash

FORBIDDEN_KEYS={"truth_facts","oracle_plan","source_plan","native_checkpoint","source_native_snapshot","evaluator_truth"}

def _hash_evidence(fact_type,subject,value,scope,evidence):
    body={"fact_type":fact_type,"subject":subject,"value":value,"scope":scope,"evidence":evidence}
    return hashlib.sha256(json.dumps(body,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

def verify_certificate(cert:dict)->bool:
    try:
        return cert.get("evidence_hash")==_hash_evidence(cert["fact_type"],cert["subject"],cert.get("value"),cert["scope"],cert.get("evidence",{}))
    except Exception:
        return False

def load_schema(root:Path): return json.loads((root/'schemas'/'mcc_v3.schema.json').read_text(encoding='utf-8'))
def validate_payload(payload:dict,root:Path):
    Draft202012Validator(load_schema(root)).validate(payload)
    def scan(x,path='$'):
        if isinstance(x,dict):
            for k,v in x.items():
                if k in FORBIDDEN_KEYS: raise ValueError(f'forbidden MCC v3 key {k!r} at {path}')
                scan(v,path+'.'+k)
        elif isinstance(x,list):
            for i,v in enumerate(x): scan(v,f'{path}[{i}]')
    scan(payload); return True

def build_mcc_v3(capture:dict,target_runtime:str,workflow_spec_hash:str,contract:dict,root:Path)->dict:
    payload={
      "mcc_version":"3.0","case_id":capture["case_id"],"workflow":capture["workflow"],
      "source_runtime":capture["native_observation"].get("framework","semantic"),"target_runtime":target_runtime,
      "workflow_spec_hash":workflow_spec_hash,"continuation_contract_hash":contract_hash(contract),
      "app_state":copy.deepcopy(capture["app_state"]),"history":copy.deepcopy(capture["history"]),"certificates":copy.deepcopy(capture["certificates"])
    }
    validate_payload(payload,root); return payload

def _canon(subject:str,bindings:dict[str,str])->str:
    seen=set(); cur=subject
    while cur in bindings and cur not in seen:
        seen.add(cur); cur=bindings[cur]
    return cur

def resolve_proofs(payload:dict,contract:dict,root:Path)->tuple[ProofState,dict]:
    validate_payload(payload,root)
    if payload.get('continuation_contract_hash')!=contract_hash(contract):
        ps=ProofState(); ps.unresolved.append({"type":"CONTRACT_HASH_MISMATCH"}); return ps,{"admissible":False,"reason":"CONTRACT_HASH_MISMATCH"}
    ps=ProofState(); raw=[]; snapshots=[]
    # First pass: verify attestations and collect identity bindings.
    for c in payload.get('certificates',[]):
        if not verify_certificate(c):
            ps.invalid_attestations.append(c.get('certificate_id','unknown')); continue
        if c.get('fact_type')=='identity_binding': ps.bindings[str(c.get('subject'))]=str(c.get('value'))
    # History -> raw facts. Deliberately no benchmark family imports here.
    for e in payload.get('history',[]):
        typ=e.get('type'); u=e.get('semantic_unit'); d=e.get('data',{})
        if typ=='tool_call_observed':
            op=d.get('operation') or e.get('step'); st=d.get('commit_status')
            if op and st in {'committed','not_committed'}: raw.append(('effect_status',op,st,'history'))
        elif typ=='semantic_unit_completed' and u: raw.append(('semantic_completion',u,'completed','history'))
        elif typ=='approval_requested':
            rid=d.get('request_id');
            if rid: raw.append(('approval_state',rid,'pending','history'))
        elif typ=='callback_pending':
            cid=d.get('callback_id');
            if cid: raw.append(('callback_state',cid,'pending','history'))
        elif typ=='compensation_required':
            a=d.get('compensation_action') or u
            if a: raw.append(('compensation_state',a,'pending','history'))
        elif typ=='decision_made': raw.append(('decision_state',str(d.get('key','route')),d.get('choice'),'history'))
        elif typ=='counter_observed': raw.append(('counter_state',str(d.get('key')),int(d.get('value',0)),'history'))
        elif typ=='retry_failed':
            if u:
                raw.append(('retry_current',u,int(d.get('attempt',0)),'history'))
                if 'max_attempts' in d: raw.append(('retry_bound',u,int(d.get('max_attempts',0)),'history'))
        elif typ=='join_observed' and u: raw.append(('dependency_state',u,list(d.get('requires',[])),'history'))
    # Verified certificates -> raw facts/snapshots.
    for c in payload.get('certificates',[]):
        if not verify_certificate(c): continue
        ft,sub,val,ev=c.get('fact_type'),str(c.get('subject')),c.get('value'),c.get('evidence',{})
        if ft=='identity_binding': continue
        if ft=='effect_commitment': raw.append(('effect_status',sub,val,'certificate'))
        elif ft=='semantic_completion': raw.append(('semantic_completion',sub,val,'certificate'))
        elif ft=='obligation_state':
            kind=ev.get('kind','obligation'); raw.append((f'{kind}_state',sub,val,'certificate'))
        elif ft=='dependency_state': raw.append(('dependency_state',sub,val,'certificate'))
        elif ft in {'counter_state','counter_bound','retry_current','retry_bound','decision_state','approval_state','callback_state','compensation_state'}: raw.append((ft,sub,val,'certificate'))
        elif ft in {'completion_snapshot','obligation_snapshot'}: snapshots.append((ft,sub,val,ev,'certificate'))
        elif ft=='fact_value': raw.append((str(ev.get('fact_type')),sub,val,'certificate'))
    # Canonicalize direct facts after bindings are known.
    def add_fact(ft,sub,val,prov):
        sub=_canon(str(sub),ps.bindings); k=f'{ft}|{sub}'
        if k in ps.facts and ps.facts[k]!=val:
            ps.conflicts.append({"type":"CONFLICTING_FACT","fact_type":ft,"subject":sub,"values":[ps.facts[k],val]}); return
        ps.facts[k]=copy.deepcopy(val); ps.provenance.setdefault(k,[]).append(prov)
    for ft,sub,val,prov in raw: add_fact(ft,sub,val,prov)
    # Closed-world snapshots can prove both positive and negative membership.
    for ft,scope,val,ev,prov in snapshots:
        if not isinstance(val,dict) or not bool(val.get('complete')): continue
        members=[_canon(str(x),ps.bindings) for x in val.get('members',[])]
        universe=[_canon(str(x),ps.bindings) for x in val.get('universe',[])]
        if ft=='completion_snapshot':
            for x in universe: add_fact('semantic_completion',x,'completed' if x in members else 'not_completed',prov+':complete_snapshot')
        else:
            kind=str(val.get('kind') or ev.get('kind') or 'obligation')
            for x in universe: add_fact(f'{kind}_state',x,'pending' if x in members else 'absent',prov+':complete_snapshot')
    # Any invalid attestation is rejection-worthy: a target must not silently ignore tampering.
    if ps.invalid_attestations: ps.unresolved.append({"type":"INVALID_ATTESTATION","ids":list(ps.invalid_attestations)})
    if ps.conflicts: ps.unresolved.extend(copy.deepcopy(ps.conflicts))
    # Closed-world admissibility: every declared continuation-critical fact must be proven.
    for req in contract.get('required_facts',[]):
        ft,sub=req['fact_type'],_canon(str(req['subject']),ps.bindings); k=f'{ft}|{sub}'
        if k not in ps.facts:
            ps.unresolved.append({"type":"UNPROVEN_REQUIRED_FACT","fact_type":ft,"subject":sub,"purpose":req.get('purpose','')})
    ok=not ps.unresolved
    reason='' if ok else ';'.join(sorted({x.get('type','UNRESOLVED') for x in ps.unresolved}))
    return ps,{"admissible":ok,"reason":reason,"unresolved":copy.deepcopy(ps.unresolved),"bindings":dict(ps.bindings),"provenance":copy.deepcopy(ps.provenance)}
