from __future__ import annotations
from collections import defaultdict
from typing import Dict, Any, Set
from .types import Decision, Resolution, RejectReason, RuntimeContext
from .certificates import verify_authenticated, verify_hash_only, DEFAULT_TEST_KEY
from .runtime_repr import validate_mapping

class ProofCarryEngine:
    def __init__(self, *, authentication=True, closed_world=True, identity_binding=True,
                 complete_snapshot=True, dependency_reasoning=True, certificate_verification=True,
                 key: bytes=DEFAULT_TEST_KEY):
        self.authentication=authentication
        self.closed_world=closed_world
        self.identity_binding=identity_binding
        self.complete_snapshot=complete_snapshot
        self.dependency_reasoning=dependency_reasoning
        self.certificate_verification=certificate_verification
        self.key=key

    def resolve(self, case: Dict[str,Any], contract: Dict[str,Any], evidence: Dict[str,Any],
                used_nonces: Set[str] | None=None, consume_nonces=False) -> Resolution:
        used_nonces = used_nonces if used_nonces is not None else set()
        ctx=RuntimeContext(case['workflow_id'],case['execution_id'],evidence['source_runtime'],evidence['target_runtime'],contract['contract_hash'])
        values=defaultdict(list); rejected=[]
        for k,v in evidence.get('history',{}).items(): values[k].append(v)
        for group,snap in evidence.get('snapshots',{}).items():
            if not snap.get('complete',False):
                if self.complete_snapshot and group in contract.get('required_snapshots',[]):
                    return Resolution(Decision.REJECT,None,RejectReason.INCOMPLETE_SNAPSHOT.value,{},details={'snapshot':group})
                continue
            if self.complete_snapshot:
                for k,v in snap.get('members',{}).items(): values[k].append(v)
        for cert in evidence.get('certificates',[]):
            ok=True; reason=None
            if self.certificate_verification:
                if self.authentication:
                    ok,reason=verify_authenticated(cert,ctx,self.key,used_nonces,consume_nonce=consume_nonces)
                else:
                    ok,reason=verify_hash_only(cert,ctx,used_nonces,consume_nonce=consume_nonces)
            if not ok:
                rejected.append(reason or RejectReason.INVALID_CERTIFICATE.value)
                return Resolution(Decision.REJECT,None,reason or RejectReason.INVALID_CERTIFICATE.value,{},rejected)
            values[cert.get('subject')].append(cert.get('value'))
        if self.identity_binding and not validate_mapping(case,evidence['source_runtime'],evidence['target_runtime'],evidence.get('identity_mapping',{})):
            return Resolution(Decision.REJECT,None,RejectReason.IDENTITY_MISMATCH.value,{},rejected)
        resolved={}
        for f in contract['required_facts']:
            name=f['name']; vals=values.get(name,[])
            uniq=[]
            for v in vals:
                if v not in uniq: uniq.append(v)
            if len(uniq)>1:
                return Resolution(Decision.REJECT,None,RejectReason.CONTRADICTORY_FACT.value,resolved,rejected,{'fact':name,'values':uniq})
            if not uniq:
                if self.closed_world:
                    return Resolution(Decision.REJECT,None,RejectReason.MISSING_FACT.value,resolved,rejected,{'fact':name})
                resolved[name]=False
            else:
                resolved[name]=uniq[0]
            if f.get('role')=='guard' and resolved[name] != f.get('required_value'):
                return Resolution(Decision.REJECT,None,RejectReason.CONTRADICTORY_FACT.value,resolved,rejected,{'fact':name})
        if self.dependency_reasoning:
            for dep in contract.get('dependencies',[]):
                vals=values.get(dep['requires'],[])
                uniq=[]
                for v in vals:
                    if v not in uniq: uniq.append(v)
                if len(uniq)!=1 or uniq[0] != dep.get('expected',True):
                    return Resolution(Decision.REJECT,None,RejectReason.DEPENDENCY_UNRESOLVED.value,resolved,rejected,{'dependency':dep})
        rule=contract['decision_rule']; dv=resolved.get(rule['fact'])
        if not isinstance(dv,bool):
            return Resolution(Decision.REJECT,None,RejectReason.CONTRADICTORY_FACT.value,resolved,rejected,{'fact':rule['fact'],'value':dv})
        plan=rule['plan_if_true'] if dv else rule['plan_if_false']
        return Resolution(Decision.CONTINUE,plan,None,resolved,rejected)
