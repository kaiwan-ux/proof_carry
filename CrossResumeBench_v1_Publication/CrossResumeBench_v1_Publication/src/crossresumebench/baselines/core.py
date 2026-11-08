from __future__ import annotations
from copy import deepcopy
from ..models import RuntimeState, TransferPackage
from ..inference import reconstruct_from_history

CRITICAL_EFFECT_FAMILIES={"effect_then_reject_branch","two_effects_one_ambiguous","parallel_two_effects_partial","nested_loop_retry_effect","callback_after_commit","compensation_after_partial_parallel","one_to_many_mapping","many_to_one_mapping","branch_join_pending_tool"}

def _src(case): return RuntimeState.from_dict(case.source_state)
def _pkg(name,payload,**kw): return TransferPackage(name,payload,**kw)
def _state_payload(s): return {"case_id":s.case_id,"workflow":s.workflow,"app_state":deepcopy(s.app_state)}

def build_transfer(name,case):
    s=_src(case); g=case.static_graph
    if name=="state_only":
        return _pkg(name,_state_payload(s))
    if name=="native_restart":
        p=_state_payload(s); p["restart_from_beginning"]=True; return _pkg(name,p)
    if name=="raw_history":
        p=_state_payload(s); p["history"]=deepcopy(s.history); return _pkg(name,p)
    if name=="history_inference":
        imp,rep=reconstruct_from_history(s.case_id,s.workflow,s.app_state,s.history,g,{})
        if rep["ambiguities"] and s.workflow in CRITICAL_EFFECT_FAMILIES:
            return _pkg(name,{"state":imp.to_dict()},inference_report=rep,accepted=False,reject_reason="AMBIGUOUS_EXTERNAL_COMMIT")
        return _pkg(name,{"state":imp.to_dict()},inference_report=rep)
    if name=="mcc":
        # Frozen proposed mechanism: portable semantic history + certified effect receipts + reconstruction + reject-on-unknown.
        imp,rep=reconstruct_from_history(s.case_id,s.workflow,s.app_state,s.history,g,s.effect_receipts)
        unresolved=[a for a in rep["ambiguities"] if a.get("operation") not in s.effect_receipts]
        if unresolved: return _pkg(name,{"history":s.history,"effect_receipts":s.effect_receipts},inference_report=rep,accepted=False,reject_reason="UNPROVEN_CRITICAL_FACT")
        return _pkg(name,{"history":deepcopy(s.history),"effect_receipts":deepcopy(s.effect_receipts),"state":imp.to_dict()},inference_report=rep)
    if name=="explicit_minimal":
        p=_state_payload(s); p["state"]=RuntimeState(s.case_id,s.workflow,s.app_state,completed_steps=deepcopy(s.completed_steps),frontier=deepcopy(s.frontier),pending_obligations=deepcopy(s.pending_obligations),effect_receipts=deepcopy(s.effect_receipts),contract=deepcopy(s.contract),retry_counts=deepcopy(s.retry_counts),decisions=deepcopy(s.decisions),loop_counters=deepcopy(s.loop_counters)).to_dict(); return _pkg(name,p)
    if name=="full_pcc":
        return _pkg(name,{"state":s.to_dict()})
    if name=="oracle":
        return _pkg(name,{"state":s.to_dict(),"oracle":True})
    if name=="caplease_inspired":
        # Reference abstraction, NOT the CapLease authors' implementation.
        p=_state_payload(s); p["effect_receipts"]=deepcopy(s.effect_receipts); return _pkg(name,p)
    if name=="aaif_state_strict":
        # Reference projection of AAIF v3 agent-state concepts; NOT an official AAIF runtime.
        pending=[]
        for e in s.history:
            if e.get("type")=="tool_call_observed": pending.append({"tool_call_id":e.get("step"),"status":"awaiting_tool_result"})
        p={"case_id":s.case_id,"workflow":s.workflow,"app_state":deepcopy(s.app_state),"status":"migrating","iteration":max(s.loop_counters.values(),default=0),"pipeline_position":{"current_step":s.frontier.get("next"),"completed_steps":deepcopy(s.completed_steps),"remaining_steps":[]},"pending_tool_calls":pending,"conversation":deepcopy(s.history)}
        # Strict consumer refuses ambiguous pending effects rather than reissuing blindly.
        if pending and any(e.get("data",{}).get("commit_status")=="unknown" for e in s.history if e.get("type")=="tool_call_observed"):
            return _pkg(name,p,accepted=False,reject_reason="AAIF_REFERENCE_AMBIGUOUS_PENDING_TOOL")
        return _pkg(name,p)
    if name=="aaif_plus_caplease":
        aa=build_transfer("aaif_state_strict",case); p=deepcopy(aa.payload); p["effect_receipts"]=deepcopy(s.effect_receipts)
        # Durable effect evidence resolves the specific ambiguous pending-tool reason.
        return _pkg(name,p,accepted=True)
    raise KeyError(name)

def lower_transfer(pkg,case):
    s0=_src(case); p=pkg.payload
    if not pkg.accepted: return None
    if "state" in p: return RuntimeState.from_dict(p["state"])
    if pkg.name=="aaif_plus_caplease":
        # Use AAIF pipeline fields for progress + durable receipts. Rich conversation acts as portable event history.
        imp,rep=reconstruct_from_history(s0.case_id,s0.workflow,p.get("app_state",{}),p.get("conversation",[]),case.static_graph,p.get("effect_receipts",{})); pkg.inference_report=rep; return imp
    if pkg.name=="aaif_state_strict":
        st=RuntimeState(s0.case_id,s0.workflow,p.get("app_state",{}),completed_steps=p.get("pipeline_position",{}).get("completed_steps",[]),frontier={"next":p.get("pipeline_position",{}).get("current_step")},history=p.get("conversation",[])); return st
    if pkg.name=="caplease_inspired":
        return RuntimeState(s0.case_id,s0.workflow,p.get("app_state",{}),effect_receipts=p.get("effect_receipts",{}))
    if pkg.name=="raw_history":
        return RuntimeState(s0.case_id,s0.workflow,p.get("app_state",{}),history=p.get("history",[]))
    if pkg.name=="native_restart" or pkg.name=="state_only":
        return RuntimeState(s0.case_id,s0.workflow,p.get("app_state",{}))
    raise KeyError(pkg.name)
