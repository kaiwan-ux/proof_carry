from __future__ import annotations
from copy import deepcopy
from typing import Any
from .models import ExecutionState

# These are HOLD-OUT combination workflows. None is one of the six single-factor PCC-v0 workflows.
SCENARIOS = [
    "branch_effect_approval",
    "loop_effect",
    "parallel_retry_join",
    "retry_effect_uncertain",
    "approval_loop",
    "saga_compensation",
    "nested_parallel_effect",
    "branch_parallel_merge",
]

STATIC_SPECS: dict[str, dict[str, Any]] = {
    "branch_effect_approval": {"nodes":["start","decide","reserve","approval","finalize"],"edges":[["start","decide"],["decide","reserve"],["reserve","approval"],["approval","finalize"]]},
    "loop_effect": {"nodes":["start","loop","finish"],"loop_limit":3,"effect":"write_item"},
    "parallel_retry_join": {"nodes":["start","fanout","a","b","join","finish"],"join_requires":["a","b"]},
    "retry_effect_uncertain": {"nodes":["start","charge","verify","finish"],"max_retries":2},
    "approval_loop": {"nodes":["start","loop","approval","finish"],"loop_limit":3},
    "saga_compensation": {"nodes":["start","debit","credit","compensate","finish"],"saga":True},
    "nested_parallel_effect": {"nodes":["start","fanout","a_effect","b_retry","join","finish"],"join_requires":["a_effect","b_retry"]},
    "branch_parallel_merge": {"nodes":["start","decide","fanout","left_a","left_b","merge","finish"],"join_requires":["left_a","left_b"]},
}


def initial_state(workflow: str) -> ExecutionState:
    return ExecutionState(workflow=workflow, request_id=f"min-{workflow}-001", inputs={"route":"left","loop_limit":3,"amount":100})


def _receipt(s: ExecutionState, ledger: dict[str,int], op: str, *, observed_ack: bool, idempotent: bool=True) -> None:
    ledger[op] = ledger.get(op, 0) + 1
    s.effect_receipts[op] = {"operation_id":f"{s.request_id}:{op}","status":"committed","replay":"forbidden","idempotency_key":f"idem:{s.request_id}:{op}" if idempotent else None}
    if observed_ack:
        s.event("effect_commit_ack", op, operation_id=f"{s.request_id}:{op}", status="committed", replay="forbidden")
    else:
        # Honest observable history: the runtime saw a tool response/timeout, not the external transaction's true commit bit.
        s.event("tool_call_observed", op, result="returned_or_timeout", commit_status="unknown")


def source_prefix_transition(state: ExecutionState, ledger: dict[str,int]) -> ExecutionState:
    s=state.clone(); wf=s.workflow
    if wf=="branch_effect_approval":
        s.step("start"); s.decisions["route"]="left"; s.event("decision_made","decide",key="route",choice="left"); s.step("decide")
        _receipt(s,ledger,"reserve",observed_ack=False); s.step("reserve")
        s.pending_obligations=[{"type":"human_approval","request_id":"approval-1","blocks":"finalize"}]; s.event("approval_requested","approval",request_id="approval-1"); s.step("approval")
        s.control_frontier={"next":"finalize","branch":"left","blocked_on":"approval-1"}
    elif wf=="loop_effect":
        s.step("start")
        for i in (1,2):
            s.loop_counters["main"]=i; s.event("loop_iteration_completed","loop",iteration=i); _receipt(s,ledger,f"write_{i}",observed_ack=(i==1)); s.step(f"loop_{i}")
        s.control_frontier={"next":"loop_3","loop":"main","iteration":3,"limit":3}
    elif wf=="parallel_retry_join":
        s.step("start"); s.event("fanout_started","fanout",branches=["a","b"]); s.step("fanout"); s.step("a")
        s.retry_counts["b"]=1; s.event("retry_failed","b",attempt=1,max_attempts=2); s.step("b_attempt_1")
        s.pending_obligations=[{"type":"retry","step":"b","next_attempt":2,"max_attempts":2}]
        s.continuation_contract={"join":"join","requires":["a","b"],"exactly_once":["a","b"]}; s.control_frontier={"next":"b_retry_2","join":"join"}
    elif wf=="retry_effect_uncertain":
        s.step("start"); _receipt(s,ledger,"charge",observed_ack=False); s.retry_counts["charge"]=1; s.event("retry_failed","charge",attempt=1,max_attempts=2,reason="transport_timeout_after_send")
        s.pending_obligations=[{"type":"retry","step":"charge","next_attempt":2,"max_attempts":2}]
        s.continuation_contract={"effect_commit_satisfies_retry":"charge","on_committed":"verify","on_uncommitted":"retry"}; s.control_frontier={"next":"reconcile_charge"}
    elif wf=="approval_loop":
        s.step("start")
        for i in (1,2): s.loop_counters["main"]=i; s.event("loop_iteration_completed","loop",iteration=i); s.step(f"loop_{i}")
        s.pending_obligations=[{"type":"human_approval","request_id":"approval-loop","blocks":"loop_3"}]; s.event("approval_requested","approval",request_id="approval-loop")
        s.control_frontier={"next":"approval_then_loop_3","iteration":3,"limit":3}
    elif wf=="saga_compensation":
        s.step("start"); _receipt(s,ledger,"debit",observed_ack=False); s.step("debit")
        s.retry_counts["credit"]=1; s.event("retry_failed","credit",attempt=1,max_attempts=1,reason="permanent_failure"); s.step("credit_failed")
        s.pending_obligations=[{"type":"compensation","effect":"debit","action":"refund"}]
        s.continuation_contract={"saga":"compensate_on_credit_failure","compensate":"debit","with":"refund","exactly_once":True}; s.control_frontier={"next":"compensate"}
    elif wf=="nested_parallel_effect":
        s.step("start"); s.event("fanout_started","fanout",branches=["a_effect","b_retry"]); s.step("fanout")
        _receipt(s,ledger,"a_effect",observed_ack=True); s.step("a_effect")
        s.retry_counts["b_retry"]=1; s.event("retry_failed","b_retry",attempt=1,max_attempts=2); s.step("b_attempt_1")
        s.pending_obligations=[{"type":"retry","step":"b_retry","next_attempt":2,"max_attempts":2}]
        s.continuation_contract={"join":"join","requires":["a_effect","b_retry"],"exactly_once":["a_effect","b_retry"]}; s.control_frontier={"next":"b_retry_2","join":"join"}
    elif wf=="branch_parallel_merge":
        s.step("start"); s.decisions["route"]="left"; s.event("decision_made","decide",key="route",choice="left"); s.step("decide")
        s.event("fanout_started","fanout",branches=["left_a","left_b"]); s.step("fanout"); s.step("left_a")
        s.continuation_contract={"join":"merge","requires":["left_a","left_b"],"exactly_once":["left_a","left_b"],"branch":"left"}; s.control_frontier={"next":"left_b","branch":"left","join":"merge"}
    else: raise KeyError(wf)
    return s


def _has_obligation(s: ExecutionState, typ: str, **match) -> bool:
    for x in s.pending_obligations:
        if x.get("type")!=typ: continue
        if all(x.get(k)==v for k,v in match.items()): return True
    return False


def _committed(s: ExecutionState, op: str) -> bool:
    r=s.effect_receipts.get(op,{})
    return r.get("status")=="committed" and r.get("replay")=="forbidden"


def _do_effect_if_needed(s: ExecutionState, ledger: dict[str,int], op: str) -> None:
    if not _committed(s,op):
        ledger[op]=ledger.get(op,0)+1; s.event("effect_executed_target",op,count=ledger[op]); s.step(op)


def continuation_transition(state: ExecutionState, ledger: dict[str,int]) -> ExecutionState:
    s=state.clone(); wf=s.workflow
    if wf=="branch_effect_approval":
        branch=s.control_frontier.get("branch") or s.decisions.get("route") or "right"
        if branch!="left": s.step("right_fallback")
        _do_effect_if_needed(s,ledger,"reserve")
        if _has_obligation(s,"human_approval"):
            s.event("approval_resolved","approval",approved=True); s.pending_obligations=[x for x in s.pending_obligations if x.get("type")!="human_approval"]
        s.step("finalize"); s.terminated=True; s.outcome="left_reserved_approved" if branch=="left" else "wrong_branch"
    elif wf=="loop_effect":
        nxt=int(s.control_frontier.get("iteration",1))
        for i in range(nxt,4):
            s.loop_counters["main"]=i; _do_effect_if_needed(s,ledger,f"write_{i}"); s.event("loop_iteration_completed","loop",iteration=i); s.step(f"loop_{i}")
        s.step("finish"); s.terminated=True; s.outcome="done"
    elif wf=="parallel_retry_join":
        if _has_obligation(s,"retry",step="b") or s.retry_counts.get("b",0)>=1:
            s.retry_counts["b"]=2; s.event("retry_succeeded","b",attempt=2); s.step("b")
        else:
            s.event("retry_failed","b",attempt=1); s.step("b_attempt_1"); s.event("retry_succeeded","b",attempt=2); s.step("b")
        c=s.continuation_contract
        if c.get("requires")==["a","b"]:
            s.step("join")
        else:
            s.step("a"); s.step("join")
        s.step("finish"); s.terminated=True; s.outcome="done"
    elif wf=="retry_effect_uncertain":
        rule=s.continuation_contract.get("effect_commit_satisfies_retry")
        if rule=="charge" and _committed(s,"charge"):
            s.event("retry_cancelled_by_receipt","charge")
        else:
            _do_effect_if_needed(s,ledger,"charge")
        s.step("verify"); s.step("finish"); s.terminated=True; s.outcome="done"
    elif wf=="approval_loop":
        if _has_obligation(s,"human_approval"):
            s.event("approval_resolved","approval",approved=True)
        nxt=int(s.control_frontier.get("iteration",1))
        for i in range(nxt,4): s.loop_counters["main"]=i; s.event("loop_iteration_completed","loop",iteration=i); s.step(f"loop_{i}")
        s.step("finish"); s.terminated=True; s.outcome="done"
    elif wf=="saga_compensation":
        if s.continuation_contract.get("saga")=="compensate_on_credit_failure" and _has_obligation(s,"compensation",effect="debit"):
            _do_effect_if_needed(s,ledger,"refund"); s.step("compensate")
        else:
            # Unsafe default: retry debit path because the saga obligation is unknown.
            _do_effect_if_needed(s,ledger,"debit")
        s.step("finish"); s.terminated=True; s.outcome="compensated" if ledger.get("refund",0)==1 else "unsafe"
    elif wf=="nested_parallel_effect":
        _do_effect_if_needed(s,ledger,"a_effect")
        if _has_obligation(s,"retry",step="b_retry") or s.retry_counts.get("b_retry",0)>=1:
            s.retry_counts["b_retry"]=2; s.event("retry_succeeded","b_retry",attempt=2); s.step("b_retry")
        else:
            s.step("b_attempt_1"); s.step("b_retry")
        if s.continuation_contract.get("requires")==["a_effect","b_retry"]: s.step("join")
        else: s.step("a_effect"); s.step("join")
        s.step("finish"); s.terminated=True; s.outcome="done"
    elif wf=="branch_parallel_merge":
        branch=s.control_frontier.get("branch") or s.decisions.get("route") or "right"
        if branch!="left": s.step("right_action")
        c=s.continuation_contract
        if c.get("requires")==["left_a","left_b"] and branch=="left": s.step("left_b"); s.step("merge")
        else: s.step("left_a"); s.step("left_b"); s.step("merge")
        s.step("finish"); s.terminated=True; s.outcome="left_done" if branch=="left" else "wrong_branch"
    else: raise KeyError(wf)
    return s


def static_spec(workflow: str) -> dict[str,Any]: return deepcopy(STATIC_SPECS[workflow])
