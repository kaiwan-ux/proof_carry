from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any
from .certificates import digest_payload, issue_certificate, DEFAULT_TEST_KEY
from .contracts import contract_from_case
from .types import RuntimeContext
from .evidence import build_evidence
from .runtime_repr import identity_mapping

def _decision_certificate(case, source, target, evidence, key=DEFAULT_TEST_KEY):
    """Make the decision-critical fact certificate-backed for the security test.

    This prevents a correct history copy from masking a forged certificate and lets
    the experiment test whether authentication actually protects the decision.
    """
    contract=contract_from_case(case)
    ctx=RuntimeContext(case['workflow_id'],case['execution_id'],source,target,contract['contract_hash'])
    subject=case['required_facts'][0]['name']
    # Remove alternate copies of the decision fact.
    evidence['history'].pop(subject,None)
    for s in evidence.get('snapshots',{}).values(): s.get('members',{}).pop(subject,None)
    existing=[c for c in evidence.get('certificates',[]) if c.get('subject')==subject]
    evidence['certificates']=[c for c in evidence.get('certificates',[]) if c.get('subject')!=subject]
    if existing:
        cert=existing[0]
    else:
        cert=issue_certificate(subject=subject,value=True,context=ctx,nonce=f"security:{case['case_id']}:{source}:{target}:decision",key=key)
    evidence['certificates'].insert(0,cert)
    return cert,ctx

def _replace_decision_cert(ev, cert):
    ev['certificates'][0]=cert

def make_attack(case: Dict[str,Any], source: str, target: str, attack: str, key=DEFAULT_TEST_KEY):
    ev=build_evidence(case,source,target,'enough',key)
    cert,ctx=_decision_certificate(case,source,target,ev,key)
    subject=cert['subject']
    if attack == 'certificate_forgery':
        cert['value']=False  # no digest/mac update
    elif attack == 'rehashed_forgery':
        cert['value']=False
        cert['digest']=digest_payload(cert)  # attacker can rehash, cannot forge HMAC
    elif attack == 'replay':
        old_ctx=RuntimeContext(case['workflow_id'],case['execution_id']+'::OLD',source,target,ctx.contract_hash)
        _replace_decision_cert(ev,issue_certificate(subject=subject,value=False,context=old_ctx,nonce=f"replay:{case['case_id']}",key=key))
    elif attack == 'wrong_workflow':
        wrong_ctx=RuntimeContext(case['workflow_id']+'::OTHER',case['execution_id'],source,target,ctx.contract_hash)
        _replace_decision_cert(ev,issue_certificate(subject=subject,value=False,context=wrong_ctx,nonce=f"wrongwf:{case['case_id']}",key=key))
    elif attack == 'wrong_execution':
        wrong_ctx=RuntimeContext(case['workflow_id'],case['execution_id']+'::B',source,target,ctx.contract_hash)
        _replace_decision_cert(ev,issue_certificate(subject=subject,value=False,context=wrong_ctx,nonce=f"wrongexec:{case['case_id']}",key=key))
    elif attack == 'runtime_substitution':
        wrong_ctx=RuntimeContext(case['workflow_id'],case['execution_id'],source,source,ctx.contract_hash)
        _replace_decision_cert(ev,issue_certificate(subject=subject,value=False,context=wrong_ctx,nonce=f"wrongrt:{case['case_id']}",key=key))
    elif attack == 'unauthorized_identity_binding':
        ev['identity_mapping']=identity_mapping(case,source,target,'wrong')
    elif attack == 'expired_certificate':
        _replace_decision_cert(ev,issue_certificate(subject=subject,value=False,context=ctx,nonce=f"expired:{case['case_id']}",ttl_seconds=-60,key=key))
    elif attack == 'nonce_reuse':
        pass
    elif attack == 'valid_control':
        pass
    else:
        raise ValueError(attack)
    return ev

ATTACKS=(
    'certificate_forgery','rehashed_forgery','replay','wrong_workflow','wrong_execution',
    'runtime_substitution','unauthorized_identity_binding','expired_certificate','nonce_reuse',
)
