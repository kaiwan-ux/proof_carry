from __future__ import annotations
from ..models import ReconstructedContinuation

def project(capture,case):
    # Concept-level AAIF-like projection. It intentionally does not call MCC reconstruction.
    completed=[]; pending=[]; current=None
    for e in capture.portable_history:
        if e.get("type")=="semantic_unit_completed":
            u=e.get("semantic_unit");
            if u and u not in completed: completed.append(u)
        elif e.get("type") in {"approval_requested","callback_pending"}: pending.append(e)
    for a in case.target_actions:
        if a.get("semantic_unit") not in completed: current=a.get("semantic_unit"); break
    return {"version":"aaif-reference-v2","app_state":capture.app_state,"pipeline":{"completed_semantics":completed,"current_semantic":current},"pending":pending,"conversation":capture.portable_history}

def lower(proj,capture,case,effect_receipts=None):
    rc=ReconstructedContinuation(capture.case_id,capture.workflow,dict(proj.get("app_state",{})),completed_units=list(proj.get("pipeline",{}).get("completed_semantics",[])))
    for k,v in case.target_dependencies.items(): rc.dependencies[k]=list(v)
    for op,cert in (effect_receipts or {}).items(): rc.effect_facts[op]=dict(cert)
    # AAIF reference has no generic proof that unobserved parent semantic units are complete.
    return rc
