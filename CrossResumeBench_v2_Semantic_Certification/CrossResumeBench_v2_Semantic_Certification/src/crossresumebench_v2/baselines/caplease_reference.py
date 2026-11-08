from __future__ import annotations
from ..models import ReconstructedContinuation

def effect_ledger_from_certificates(capture):
    out={}
    for c in capture.certificates:
        if c.get("fact_type")=="effect_commitment": out[c.get("subject")]={"status":c.get("value"),"source":"caplease_reference","evidence":c.get("evidence",{})}
    return out

def lower(capture,case):
    rc=ReconstructedContinuation(capture.case_id,capture.workflow,dict(capture.app_state)); rc.effect_facts=effect_ledger_from_certificates(capture)
    return rc
