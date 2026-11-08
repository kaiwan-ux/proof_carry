from __future__ import annotations
from .frozen import SourceCapture, issue_certificate
from .semantics import SAFE_APP_STATE, truth_projection


def _cert(case,fact_type,subject,value,evidence):
    return issue_certificate(case.case_id,fact_type,subject,value,case.case_id,evidence).to_dict()

def history_and_certs(case,variant,native):
    p=case.params; f=case.family; h=[]; certs=[]
    if variant not in case.applicable_variants: raise ValueError(f"variant {variant} not applicable to {case.case_id}")
    if f=="effect_commitment":
        h=[{"type":"tool_call_observed","semantic_unit":"effect_attempt","data":{"operation":p["operation"],"commit_status":"unknown","parent_unit":"effect_attempt","unit_completion_observable":True}}]
        if variant=="enough_evidence": certs=[_cert(case,"effect_commitment",p["operation"],p["effect_status"],{"native_checkpoint_ref":native.checkpoint_ref,"idempotency_key":f"{case.case_id}:{p['operation']}"})]
    elif f=="retry_pause":
        unit="retry_task" if variant!="conflicting_granularity" else "source_retry_task"
        data={"attempt":p["current_attempt"]}
        if variant!="partially_observable_progress": data["max_attempts"]=p["max_attempts"]
        h=[{"type":"retry_failed","semantic_unit":unit,"data":data}]
    elif f=="approval_wait":
        if variant=="enough_evidence":
            h=[{"type":"approval_requested","semantic_unit":p["approval_unit"],"data":{"request_id":p["request_id"],"blocks":p["approval_unit"]}}]
            certs=[_cert(case,"obligation_state",p["request_id"],"pending",{"kind":"approval","blocks":p["approval_unit"],"native_checkpoint_ref":native.checkpoint_ref})]
    elif f=="parallel_join":
        h=[{"type":"join_observed","semantic_unit":p["join"],"data":{"requires":list(p["branches"])}}]
        cb=p["certified_branch"]
        for b in p["completed"]:
            if b!=cb: h.append({"type":"semantic_unit_completed","semantic_unit":b,"data":{}})
        if variant in {"enough_evidence","missing_semantic_completion","conflicting_granularity"}:
            h.append({"type":"tool_call_observed","semantic_unit":cb,"data":{"operation":"branch_marker","commit_status":"unknown","parent_unit":cb,"unit_completion_observable":False}})
        if variant=="enough_evidence":
            certs=[_cert(case,"semantic_completion",cb,"completed",{"native_checkpoint_ref":native.checkpoint_ref}),_cert(case,"dependency_state",p["join"],list(p["branches"]),{"native_checkpoint_ref":native.checkpoint_ref})]
        elif variant=="conflicting_granularity":
            certs=[_cert(case,"semantic_completion",f"source_{cb}","completed",{"native_checkpoint_ref":native.checkpoint_ref})]
    elif f=="loop_pause":
        key=p["counter_key"] if variant!="conflicting_granularity" else "source_loop_index"
        if variant!="partially_observable_progress": h.append({"type":"counter_observed","data":{"key":key,"value":p["current"]}})
        if p.get("break"): h.append({"type":"decision_made","data":{"key":"break","choice":True}})
    elif f=="compensation_pending":
        h=[{"type":"tool_call_observed","semantic_unit":"effect_attempt","data":{"operation":p["operation"],"commit_status":"unknown","parent_unit":"effect_attempt","unit_completion_observable":True}}]
        if variant!="partially_observable_progress" and p["effect_status"]=="committed": h.append({"type":"compensation_required","semantic_unit":"compensation","data":{"compensation_action":p["compensation"],"effect":p["operation"]}})
        if variant!="ambiguous_external_commit": certs=[_cert(case,"effect_commitment",p["operation"],p["effect_status"],{"native_checkpoint_ref":native.checkpoint_ref})]
    elif f=="async_callback":
        if variant!="partially_observable_progress":
            op=p["operation"] if variant!="conflicting_granularity" else f"source_{p['operation']}"
            h=[{"type":"callback_pending","semantic_unit":p["callback_unit"],"data":{"callback_id":p["callback_id"],"operation":op,"blocks":p["callback_unit"]}}]
            if variant=="enough_evidence": certs=[_cert(case,"obligation_state",p["callback_id"],"pending",{"kind":"callback","blocks":p["callback_unit"],"native_checkpoint_ref":native.checkpoint_ref})]
    return h,certs

def source_capture(case,native,variant):
    h,certs=history_and_certs(case,variant,native); truth=truth_projection(case)
    obs=dict(native.native_observation); obs["framework"]=native.framework
    effects={op:int(count) for op,count in native.source_store.get("effects",{}).items()}
    return SourceCapture(case.case_id,f"full_v3_{case.family}",dict(SAFE_APP_STATE),h,certs,effects,obs,list(truth["completed"]),list(truth["pending"]),dict(truth["dependencies"]),dict(truth["decisions"]),dict(truth["counters"]))
