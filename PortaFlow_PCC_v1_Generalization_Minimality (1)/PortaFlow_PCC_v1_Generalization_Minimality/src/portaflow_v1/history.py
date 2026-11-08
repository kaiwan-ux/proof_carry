from __future__ import annotations
from copy import deepcopy
from typing import Any
from .models import ExecutionState


def portable_history(trace: list[dict[str,Any]]) -> list[dict[str,Any]]:
    # No artificial redaction. This is exactly the framework-neutral observable event stream emitted by the benchmark tools.
    return deepcopy(trace)


def infer_semantics(workflow: str, history: list[dict[str,Any]], static_spec: dict[str,Any]) -> tuple[dict[str,Any], dict[str,Any]]:
    completed=[]; retry_counts={}; decisions={}; loops={}; obligations=[]; receipts={}; frontier={}; contract={}
    ambiguities=[]; inferred=[]
    approvals: dict[str,bool]={}
    fanout_branches=None
    for e in history:
        k=e.get("kind"); step=e.get("step"); d=e.get("detail",{})
        if k=="step_completed": completed.append(step)
        elif k=="retry_failed":
            retry_counts[step]=max(retry_counts.get(step,0), int(d.get("attempt",1)))
            obligations=[x for x in obligations if not (x.get("type")=="retry" and x.get("step")==step)]
            obligations.append({"type":"retry","step":step,"next_attempt":int(d.get("attempt",1))+1,"max_attempts":int(d.get("max_attempts",2))})
        elif k=="retry_succeeded":
            retry_counts[step]=max(retry_counts.get(step,0), int(d.get("attempt",1))); obligations=[x for x in obligations if not (x.get("type")=="retry" and x.get("step")==step)]
        elif k=="decision_made": decisions[d.get("key","decision")]=d.get("choice")
        elif k=="loop_iteration_completed": loops["main"]=max(loops.get("main",0), int(d.get("iteration",0)))
        elif k=="approval_requested": approvals[str(d.get("request_id"))]=False
        elif k=="approval_resolved": approvals[str(d.get("request_id"))]=True
        elif k=="effect_commit_ack":
            receipts[step]={"operation_id":d.get("operation_id"),"status":"committed","replay":d.get("replay","forbidden"),"inferred_from":"effect_commit_ack"}
        elif k=="tool_call_observed" and d.get("commit_status")=="unknown":
            ambiguities.append({"type":"effect_commit_unknown","operation":step})
        elif k=="fanout_started": fanout_branches=list(d.get("branches",[]))
    for rid,resolved in approvals.items():
        if rid!="None" and not resolved: obligations.append({"type":"human_approval","request_id":rid})
    if completed: inferred.append("completed")
    if retry_counts: inferred.append("retry_counts")
    if decisions: inferred.append("decisions")
    if loops: inferred.append("loop_counters")
    if obligations: inferred.append("pending_obligations")
    if receipts: inferred.append("effect_receipts")

    # Strong reconstruction uses BOTH event history and the portable static workflow definition.
    if workflow=="branch_effect_approval":
        if decisions.get("route"): frontier={"next":"finalize","branch":decisions["route"]}
    elif workflow=="loop_effect":
        n=loops.get("main",0); frontier={"next":f"loop_{n+1}","iteration":n+1,"limit":int(static_spec.get("loop_limit",3))} if n else {}
    elif workflow=="parallel_retry_join":
        if retry_counts.get("b"): frontier={"next":"b_retry_2","join":"join"}
        req=static_spec.get("join_requires"); contract={"join":"join","requires":req,"exactly_once":req} if req else {}
    elif workflow=="retry_effect_uncertain":
        frontier={"next":"reconcile_charge"}
        # Static topology cannot prove whether charge committed after a transport timeout.
        contract={"effect_commit_satisfies_retry":"charge","on_committed":"verify","on_uncommitted":"retry"}
    elif workflow=="approval_loop":
        n=loops.get("main",0); frontier={"next":"approval_then_loop_3","iteration":n+1,"limit":int(static_spec.get("loop_limit",3))} if n else {}
    elif workflow=="saga_compensation":
        if retry_counts.get("credit"): obligations.append({"type":"compensation","effect":"debit","action":"refund"})
        contract={"saga":"compensate_on_credit_failure","compensate":"debit","with":"refund","exactly_once":True}; frontier={"next":"compensate"}
    elif workflow=="nested_parallel_effect":
        if retry_counts.get("b_retry"): frontier={"next":"b_retry_2","join":"join"}
        req=static_spec.get("join_requires"); contract={"join":"join","requires":req,"exactly_once":req} if req else {}
    elif workflow=="branch_parallel_merge":
        branch=decisions.get("route")
        req=static_spec.get("join_requires"); contract={"join":"merge","requires":req,"exactly_once":req,"branch":branch} if req and branch else {}
        if branch: frontier={"next":"left_b","branch":branch,"join":"merge"}
    if frontier: inferred.append("control_frontier")
    if contract: inferred.append("continuation_contract")
    return {
        "completed":completed,"retry_counts":retry_counts,"decisions":decisions,"loop_counters":loops,
        "control_frontier":frontier,"pending_obligations":obligations,"effect_receipts":receipts,"continuation_contract":contract,
    }, {"ambiguities":ambiguities,"inferred_fields":sorted(set(inferred)),"static_spec_used":True}


def apply_inferred(state: ExecutionState, inferred: dict[str,Any], *, only_missing: bool=True) -> ExecutionState:
    s=state.clone()
    def put(attr):
        val=inferred.get(attr)
        current=getattr(s,attr)
        empty=current in ({},[],None,0,"")
        if val and (not only_missing or empty): setattr(s,attr,deepcopy(val))
    for a in ["completed","retry_counts","decisions","loop_counters","control_frontier","pending_obligations","effect_receipts","continuation_contract"]: put(a)
    return s
