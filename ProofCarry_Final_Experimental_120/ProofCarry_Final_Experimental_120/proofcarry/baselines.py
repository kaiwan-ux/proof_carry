from __future__ import annotations
from collections import defaultdict
from typing import Dict, Any
from .types import Decision, Resolution
from .runtime_repr import validate_mapping

# These are concept-level experimental references, not official implementations.
# They deliberately have independent decision code rather than calling ProofCarryEngine.

def always_reject(case, contract, evidence):
    return Resolution(Decision.REJECT,None,"ALWAYS_REJECT_CONTROL")

def oracle(case, contract, evidence):
    return Resolution(Decision.CONTINUE,case["safe_plan"],None,{f['name']:f['expected'] for f in case['required_facts']})

def history_only(case, contract, evidence):
    hist=evidence.get("history",{})
    # optimistic history replay: absent obligations are treated as absent/completed
    return Resolution(Decision.CONTINUE,case["safe_plan"],None,dict(hist))

def mcc_v2_frozen(case, contract, evidence):
    # Frozen-style certificate/history reconstruction without the v3 closed-world proof contract.
    vals=dict(evidence.get("history",{}))
    for c in evidence.get("certificates",[]): vals[c.get("subject")]=c.get("value")
    # catches explicit conflicts only when history and cert disagree on the same key
    for c in evidence.get("certificates",[]):
        k=c.get("subject")
        if k in evidence.get("history",{}) and evidence["history"][k] != c.get("value"):
            return Resolution(Decision.REJECT,None,"EXPLICIT_CONFLICT")
    # conservative for effect-commit ambiguity, but not a general closed-world proof of obligations
    if case["workflow_family"] == "effect_commitment" and contract["required_facts"][0]["name"] not in vals:
        return Resolution(Decision.REJECT,None,"AMBIGUOUS_EXTERNAL_COMMIT")
    return Resolution(Decision.CONTINUE,case["safe_plan"],None,vals)

def aaif_reference(case, contract, evidence):
    # Concept-level state/checkpoint portability reference: uses state/history + mapping status,
    # but does not require authenticated certified evidence or complete proof of every obligation.
    if evidence.get("identity_mapping",{}).get("status") in {"wrong","ambiguous"}:
        return Resolution(Decision.REJECT,None,"MAPPING_UNRESOLVED")
    return Resolution(Decision.CONTINUE,case["safe_plan"],None,dict(evidence.get("history",{})))

def caplease_reference(case, contract, evidence):
    # Concept-level durable-effect reference: protects effect-like families but does not model
    # every non-effect continuation obligation.
    fam=case["workflow_family"]
    if fam in {"effect_commitment","compensation","composite"}:
        first=contract["required_facts"][0]["name"]
        present= first in evidence.get("history",{}) or any(c.get("subject")==first for c in evidence.get("certificates",[]))
        if not present:
            return Resolution(Decision.REJECT,None,"EFFECT_COMMIT_UNKNOWN")
    return Resolution(Decision.CONTINUE,case["safe_plan"],None,{})

def aaif_plus_caplease_reference(case, contract, evidence):
    a=aaif_reference(case,contract,evidence)
    if a.decision == Decision.REJECT: return a
    return caplease_reference(case,contract,evidence)

BASELINES={
    "mcc_v2_frozen":mcc_v2_frozen,
    "history_only":history_only,
    "aaif_reference":aaif_reference,
    "caplease_reference":caplease_reference,
    "aaif_plus_caplease_reference":aaif_plus_caplease_reference,
    "always_reject":always_reject,
    "oracle":oracle,
}
