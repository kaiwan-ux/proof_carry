from __future__ import annotations
import json, hashlib
from .frozen import ReconstructedContinuation, TransferPackage, build_mcc_v2, reconstruct_mcc_v2, admissibility
from .semantics import truth_projection

METHODS=["mcc_v2","history_inference","aaif_reference","caplease_reference","aaif_plus_caplease_reference","explicit_minimal","oracle"]

def _hash_case(v2case):
    return hashlib.sha256(json.dumps({"target_actions":v2case.target_actions,"dependencies":v2case.target_dependencies},sort_keys=True,separators=(",",":")).encode()).hexdigest()

def _history_inference(capture,v2case):
    rc=ReconstructedContinuation(capture.case_id,capture.workflow,dict(capture.app_state)); amb=[]
    for e in capture.portable_history:
        typ=e.get("type"); u=e.get("semantic_unit"); d=e.get("data",{})
        if typ=="semantic_unit_completed" and u and u not in rc.completed_units: rc.completed_units.append(u)
        elif typ=="tool_call_observed":
            op=d.get("operation") or e.get("step")
            if d.get("commit_status") in {"committed","not_committed"}: rc.effect_facts[op]={"status":d["commit_status"],"source":"history"}
            else: amb.append({"type":"AMBIGUOUS_EXTERNAL_COMMIT","operation":op})
            if d.get("parent_unit") and not d.get("unit_completion_observable",False) and u not in rc.completed_units: amb.append({"type":"AMBIGUOUS_SEMANTIC_COMPLETION","semantic_unit":u})
        elif typ=="approval_requested": rc.pending_obligations.append({"type":"approval","id":d.get("request_id"),"blocks":d.get("blocks")})
        elif typ=="callback_pending": rc.pending_obligations.append({"type":"callback","id":d.get("callback_id"),"operation":d.get("operation"),"blocks":u})
        elif typ=="compensation_required": rc.pending_obligations.append({"type":"compensation","action":d.get("compensation_action") or u,"effect":d.get("effect")})
        elif typ=="decision_made": rc.decisions[d.get("key")]=d.get("choice")
        elif typ=="counter_observed": rc.counters[d.get("key")]=int(d.get("value",0))
        elif typ=="retry_failed": rc.counters[f"retry:{u}"]=int(d.get("attempt",0)); rc.pending_obligations.append({"type":"retry","step":u,"next_attempt":int(d.get("attempt",0))+1,"max_attempts":int(d.get("max_attempts",0))})
        elif typ=="join_observed" and u: rc.dependencies[u]=list(d.get("requires",[]))
    for k,v in v2case.target_dependencies.items(): rc.dependencies.setdefault(k,list(v))
    # Only target-relevant ambiguities cause strict history rejection.
    tops={a.get("operation") for a in v2case.target_actions if a.get("kind")=="effect" and a.get("operation")}; tunits={a.get("semantic_unit") for a in v2case.target_actions}
    rc.ambiguities=[a for a in amb if (a.get("type")!="AMBIGUOUS_EXTERNAL_COMMIT" or a.get("operation") in tops) and (a.get("type")!="AMBIGUOUS_SEMANTIC_COMPLETION" or a.get("semantic_unit") in tunits)]
    return rc

def build_and_lower(method,capture,case,v2case,target,root):
    if method=="mcc_v2":
        pkg=build_mcc_v2(capture,target,_hash_case(v2case),root); rc,rep=reconstruct_mcc_v2(pkg.payload,v2case,root); pkg.inference_report=rep; ok,reason=admissibility(rc)
        if not ok: return pkg,None,reason
        return pkg,rc,""
    if method=="history_inference":
        payload={"app_state":capture.app_state,"history":capture.portable_history}; pkg=TransferPackage(method,payload); rc=_history_inference(capture,v2case)
        if rc.ambiguities: return pkg,None,";".join(sorted({x["type"] for x in rc.ambiguities}))
        return pkg,rc,""
    if method in {"aaif_reference","aaif_plus_caplease_reference"}:
        completed=[]; pending=[]
        for e in capture.portable_history:
            if e.get("type")=="semantic_unit_completed" and e.get("semantic_unit"): completed.append(e["semantic_unit"])
            elif e.get("type") in {"approval_requested","callback_pending"}: pending.append(e)
        payload={"version":method,"app_state":capture.app_state,"completed_semantics":completed,"pending":pending,"history":capture.portable_history}
        rc=ReconstructedContinuation(capture.case_id,capture.workflow,dict(capture.app_state),completed_units=list(dict.fromkeys(completed)))
        for k,v in v2case.target_dependencies.items(): rc.dependencies[k]=list(v)
        for e in pending:
            d=e.get("data",{}); typ=e.get("type")
            if typ=="approval_requested": rc.pending_obligations.append({"type":"approval","id":d.get("request_id"),"blocks":d.get("blocks")})
            else: rc.pending_obligations.append({"type":"callback","id":d.get("callback_id"),"operation":d.get("operation")})
        if method=="aaif_plus_caplease_reference":
            for c in capture.certificates:
                if c.get("fact_type")=="effect_commitment": rc.effect_facts[c.get("subject")]={"status":c.get("value"),"source":"caplease_reference"}
        # Concept-level AAIF strict policy only rejects ambiguous external effects, matching v2 reference behavior.
        if method=="aaif_reference" and any(e.get("type")=="tool_call_observed" and e.get("data",{}).get("commit_status")=="unknown" for e in capture.portable_history): return TransferPackage(method,payload),None,"AAIF_REFERENCE_AMBIGUOUS_PENDING_EFFECT"
        return TransferPackage(method,payload),rc,""
    if method=="caplease_reference":
        payload={"app_state":capture.app_state,"effect_ledger":{}}; rc=ReconstructedContinuation(capture.case_id,capture.workflow,dict(capture.app_state))
        for c in capture.certificates:
            if c.get("fact_type")=="effect_commitment": rc.effect_facts[c.get("subject")]={"status":c.get("value"),"source":"caplease_reference"}; payload["effect_ledger"][c.get("subject")]=rc.effect_facts[c.get("subject")]
        return TransferPackage(method,payload),rc,""
    truth=truth_projection(case)
    rc=ReconstructedContinuation(capture.case_id,capture.workflow,dict(capture.app_state),list(truth["completed"]),list(truth["pending"]),{op:{"status":st,"source":"privileged_truth"} for op,st in truth["effects"].items()},dict(truth["dependencies"]),dict(truth["decisions"]),dict(truth["counters"]))
    payload={"privileged":True,"truth":truth} if method=="oracle" else {"explicit_truth":truth}
    return TransferPackage(method,payload),rc,""
