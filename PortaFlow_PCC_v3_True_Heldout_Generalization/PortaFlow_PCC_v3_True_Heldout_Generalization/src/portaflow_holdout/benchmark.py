from __future__ import annotations
from copy import deepcopy
from typing import Any
from .models import ExecutionState

# TRUE HOLD-OUT SUITE: none of these ten workflow names appeared in PCC v0/v1/v2 discovery.
SCENARIOS = [
    "inventory_callback_fulfillment",
    "multi_effect_order_dispatch",
    "quorum_parallel_2of3",
    "race_first_success_cancel",
    "nested_loop_branch_retry_v2",
    "human_edit_publish",
    "saga_dual_compensation",
    "lease_renewal_handoff",
    "mixed_idempotency_effects",
    "map_reduce_threshold",
]

STATIC_SPECS: dict[str, dict[str, Any]] = {
    "inventory_callback_fulfillment": {
        "nodes":["start","hold_inventory","await_callback","fulfill","finish"],
        "contract":{"requires_obligation":"webhook","effect_exactly_once":["hold_inventory"]},
        "frontier_rules":[{"when":{"obligation_type":"webhook"},"frontier":{"next":"await_callback_then_fulfill"}}],
    },
    "multi_effect_order_dispatch": {
        "nodes":["start","authorize_payment","create_label","dispatch","finish"],
        "contract":{"effect_exactly_once":["authorize_payment","create_label"]},
        "frontier_rules":[{"when":{},"frontier":{"next":"dispatch"}}],
    },
    "quorum_parallel_2of3": {
        "nodes":["start","fanout","worker_a","worker_b","worker_c","quorum_join","finish"],
        "contract":{"join":"quorum_join","members":["worker_a","worker_b","worker_c"],"quorum":2,"cancel_remainder":True},
        "frontier_rules":[{"when":{"obligation_type":"cancel_branch"},"frontier":{"next":"quorum_join"}}],
    },
    "race_first_success_cancel": {
        "nodes":["start","fanout","branch_fast","branch_slow_1","branch_slow_2","finish"],
        "contract":{"race":"first_success","winner":"branch_fast","cancel":["branch_slow_1","branch_slow_2"]},
        "frontier_rules":[{"when":{"completed_all":["branch_fast"]},"frontier":{"next":"cancel_losers_then_finish"}}],
    },
    "nested_loop_branch_retry_v2": {
        "nodes":["start","review_loop","decide_lane","fast_tool","slow_tool","finish"],
        "loop_limit":3,
        "contract":{"loop_id":"review","loop_limit":3,"decision_key":"lane","retry_step":"fast_tool"},
        "frontier_rules":[{"when":{"decision":{"lane":"fast"},"retry_at_least":{"fast_tool":1}},"frontier":{"next":"retry_fast_then_review_3","branch":"$decision:lane","iteration":"$loop_next:review"}}],
    },
    "human_edit_publish": {
        "nodes":["start","human_edit","approval","publish","finish"],
        "contract":{"requires_approval_before":"publish"},
        "frontier_rules":[{"when":{"obligation_type":"human_approval"},"frontier":{"next":"approval_then_publish"}}],
    },
    "saga_dual_compensation": {
        "nodes":["start","debit","reserve_stock","ship","release_stock","refund","finish"],
        "contract":{"saga":True,"compensation_order":["release_stock","refund"],"compensates":{"release_stock":"reserve_stock","refund":"debit"}},
        "frontier_rules":[{"when":{"obligation_type":"compensation"},"frontier":{"next":"compensate_reverse_order"}}],
    },
    "lease_renewal_handoff": {
        "nodes":["start","acquire_lease","renew_lease","critical_section","finish"],
        "contract":{"lease":"lease-1","renew_before":"critical_section"},
        "frontier_rules":[{"when":{"obligation_type":"lease_renewal"},"frontier":{"next":"renew_then_enter_critical"}}],
    },
    "mixed_idempotency_effects": {
        "nodes":["start","cache_write","charge","verify","finish"],
        "contract":{"idempotent":["cache_write"],"non_idempotent":["charge"],"effect_exactly_once":["charge"]},
        "frontier_rules":[{"when":{},"frontier":{"next":"verify"}}],
    },
    "map_reduce_threshold": {
        "nodes":["start","fanout","shard_1","shard_2","shard_3","shard_4","reduce","finish"],
        "contract":{"join":"reduce","members":["shard_1","shard_2","shard_3","shard_4"],"quorum":3,"cancel_remainder":True},
        "frontier_rules":[{"when":{"obligation_type":"cancel_branch"},"frontier":{"next":"reduce"}}],
    },
}


def initial_state(workflow: str) -> ExecutionState:
    return ExecutionState(workflow=workflow, request_id=f"holdout-{workflow}-001", inputs={"amount":100,"document":"draft-v1","route":"fast","logical_tick":10})


def _receipt(s: ExecutionState, ledger: dict[str,int], op: str, *, observed_ack: bool, replay: str="forbidden") -> None:
    ledger[op] = ledger.get(op, 0) + 1
    s.effect_receipts[op] = {"operation_id":f"{s.request_id}:{op}","status":"committed","replay":replay,"idempotency_key":f"idem:{s.request_id}:{op}"}
    if observed_ack:
        s.event("effect_commit_ack",op,operation_id=f"{s.request_id}:{op}",status="committed",replay=replay)
    else:
        s.event("tool_call_observed",op,result="returned_or_timeout",commit_status="unknown",replay_class="unknown")


def _open_obligation(s:ExecutionState, typ:str, oid:str, **detail:Any)->None:
    rec={"type":typ,"id":oid,**detail}; s.pending_obligations.append(rec)
    ev_detail=dict(detail)
    if "step" in ev_detail: ev_detail["obligation_step"]=ev_detail.pop("step")
    s.event("obligation_opened",typ,id=oid,**ev_detail)


def source_prefix_transition(state: ExecutionState, ledger: dict[str,int]) -> ExecutionState:
    s=state.clone(); wf=s.workflow; spec=STATIC_SPECS[wf]
    if wf=="inventory_callback_fulfillment":
        s.step("start"); _receipt(s,ledger,"hold_inventory",observed_ack=False); s.step("hold_inventory")
        _open_obligation(s,"webhook","stock-callback",blocks="fulfill"); s.control_frontier={"next":"await_callback_then_fulfill"}; s.continuation_contract=deepcopy(spec["contract"])
    elif wf=="multi_effect_order_dispatch":
        s.step("start"); _receipt(s,ledger,"authorize_payment",observed_ack=True); s.step("authorize_payment")
        _receipt(s,ledger,"create_label",observed_ack=False); s.step("create_label"); s.control_frontier={"next":"dispatch"}; s.continuation_contract=deepcopy(spec["contract"])
    elif wf=="quorum_parallel_2of3":
        s.step("start"); s.event("fanout_started","fanout",branches=["worker_a","worker_b","worker_c"]); s.step("fanout"); s.step("worker_a"); s.step("worker_b")
        _open_obligation(s,"cancel_branch","cancel-worker-c",branch="worker_c"); s.control_frontier={"next":"quorum_join"}; s.continuation_contract=deepcopy(spec["contract"])
    elif wf=="race_first_success_cancel":
        s.step("start"); s.event("fanout_started","fanout",branches=["branch_fast","branch_slow_1","branch_slow_2"]); s.step("fanout"); s.step("branch_fast"); s.event("race_winner","branch_fast")
        _open_obligation(s,"cancel_branch","cancel-slow-1",branch="branch_slow_1"); _open_obligation(s,"cancel_branch","cancel-slow-2",branch="branch_slow_2")
        s.control_frontier={"next":"cancel_losers_then_finish"}; s.continuation_contract=deepcopy(spec["contract"])
    elif wf=="nested_loop_branch_retry_v2":
        s.step("start")
        for i in (1,2): s.loop_counters["review"]=i; s.event("loop_iteration_completed","review_loop",loop_id="review",iteration=i); s.step(f"review_{i}")
        s.decisions["lane"]="fast"; s.event("decision_made","decide_lane",key="lane",choice="fast"); s.step("decide_lane")
        s.retry_counts["fast_tool"]=1; s.event("retry_failed","fast_tool",attempt=1,max_attempts=2); s.step("fast_attempt_1")
        _open_obligation(s,"retry","retry-fast",step="fast_tool",next_attempt=2,max_attempts=2)
        s.control_frontier={"next":"retry_fast_then_review_3","branch":"fast","iteration":3}; s.continuation_contract=deepcopy(spec["contract"])
    elif wf=="human_edit_publish":
        s.step("start"); s.inputs["document"]="edited-v2"; s.event("application_state_updated","human_edit",field="document",value="edited-v2"); s.step("human_edit")
        _open_obligation(s,"human_approval","publish-approval",blocks="publish"); s.control_frontier={"next":"approval_then_publish"}; s.continuation_contract=deepcopy(spec["contract"])
    elif wf=="saga_dual_compensation":
        s.step("start"); _receipt(s,ledger,"debit",observed_ack=True); s.step("debit"); _receipt(s,ledger,"reserve_stock",observed_ack=False); s.step("reserve_stock")
        s.retry_counts["ship"]=1; s.event("retry_failed","ship",attempt=1,max_attempts=1,reason="permanent"); s.step("ship_failed")
        _open_obligation(s,"compensation","release-stock",effect="reserve_stock",action="release_stock"); _open_obligation(s,"compensation","refund-debit",effect="debit",action="refund")
        s.control_frontier={"next":"compensate_reverse_order"}; s.continuation_contract=deepcopy(spec["contract"])
    elif wf=="lease_renewal_handoff":
        s.step("start"); _receipt(s,ledger,"acquire_lease",observed_ack=True); s.step("acquire_lease")
        _open_obligation(s,"lease_renewal","lease-1-renew",lease="lease-1",before="critical_section",expires_at_tick=11); s.control_frontier={"next":"renew_then_enter_critical"}; s.continuation_contract=deepcopy(spec["contract"])
    elif wf=="mixed_idempotency_effects":
        s.step("start"); _receipt(s,ledger,"cache_write",observed_ack=False,replay="allowed"); s.step("cache_write"); _receipt(s,ledger,"charge",observed_ack=False,replay="forbidden"); s.step("charge")
        s.control_frontier={"next":"verify"}; s.continuation_contract=deepcopy(spec["contract"])
    elif wf=="map_reduce_threshold":
        s.step("start"); s.event("fanout_started","fanout",branches=["shard_1","shard_2","shard_3","shard_4"]); s.step("fanout"); s.step("shard_1"); s.step("shard_2"); s.step("shard_3")
        _open_obligation(s,"cancel_branch","cancel-shard-4",branch="shard_4"); s.control_frontier={"next":"reduce"}; s.continuation_contract=deepcopy(spec["contract"])
    else: raise KeyError(wf)
    return s


def _has_obligation(s:ExecutionState, typ:str, **match)->bool:
    for x in s.pending_obligations:
        if x.get("type")!=typ: continue
        if all(x.get(k)==v for k,v in match.items()): return True
    return False

def _resolve_type(s:ExecutionState, typ:str)->None:
    xs=[x for x in s.pending_obligations if x.get("type")==typ]
    for x in xs: s.event("obligation_resolved",typ,id=x.get("id"))
    s.pending_obligations=[x for x in s.pending_obligations if x.get("type")!=typ]

def _committed(s:ExecutionState,op:str)->bool:
    return s.effect_receipts.get(op,{}).get("status")=="committed"

def _do_effect_if_needed(s:ExecutionState,ledger:dict[str,int],op:str)->None:
    r=s.effect_receipts.get(op,{})
    if r.get("status")=="committed" and r.get("replay")=="forbidden": return
    ledger[op]=ledger.get(op,0)+1; s.event("effect_executed_target",op,count=ledger[op]); s.step(op)

def continuation_transition(state:ExecutionState, ledger:dict[str,int])->ExecutionState:
    s=state.clone(); wf=s.workflow
    if wf=="inventory_callback_fulfillment":
        _do_effect_if_needed(s,ledger,"hold_inventory")
        if _has_obligation(s,"webhook"): _resolve_type(s,"webhook")
        else: s.step("callback_missing")
        s.step("fulfill"); s.step("finish"); s.terminated=True; s.outcome="fulfilled"
    elif wf=="multi_effect_order_dispatch":
        _do_effect_if_needed(s,ledger,"authorize_payment"); _do_effect_if_needed(s,ledger,"create_label"); s.step("dispatch"); s.step("finish"); s.terminated=True; s.outcome="dispatched"
    elif wf=="quorum_parallel_2of3":
        c=s.continuation_contract
        if c.get("quorum")==2 and _has_obligation(s,"cancel_branch"):
            _resolve_type(s,"cancel_branch"); s.step("quorum_join")
        else:
            s.step("worker_c"); s.step("quorum_join")
        s.step("finish"); s.terminated=True; s.outcome="quorum_done"
    elif wf=="race_first_success_cancel":
        c=s.continuation_contract
        if c.get("race")=="first_success" and len([x for x in s.pending_obligations if x.get("type")=="cancel_branch"])>=2:
            _resolve_type(s,"cancel_branch")
        else:
            s.step("branch_slow_1"); s.step("branch_slow_2")
        s.step("finish"); s.terminated=True; s.outcome="fast_won"
    elif wf=="nested_loop_branch_retry_v2":
        branch=s.control_frontier.get("branch") or s.decisions.get("lane") or "slow"
        if _has_obligation(s,"retry",step="fast_tool") or s.control_frontier.get("next")=="retry_fast_then_review_3":
            _resolve_type(s,"retry"); s.retry_counts["fast_tool"]=2; s.event("retry_succeeded","fast_tool",attempt=2); s.step("fast_tool")
        else: s.step("slow_tool")
        nxt=int(s.control_frontier.get("iteration") or (s.loop_counters.get("review",0)+1) or 1)
        if branch=="fast" and nxt==3: s.loop_counters["review"]=3; s.event("loop_iteration_completed","review_loop",loop_id="review",iteration=3); s.step("review_3")
        else: s.step("wrong_loop_or_branch")
        s.step("finish"); s.terminated=True; s.outcome="fast_review_done" if branch=="fast" else "wrong_branch"
    elif wf=="human_edit_publish":
        if _has_obligation(s,"human_approval"): _resolve_type(s,"human_approval")
        else: s.step("approval_missing")
        ledger["publish"]=ledger.get("publish",0)+1; s.event("effect_executed_target","publish",count=ledger["publish"]); s.step("publish"); s.step("finish"); s.terminated=True; s.outcome=s.inputs.get("document")
    elif wf=="saga_dual_compensation":
        _do_effect_if_needed(s,ledger,"debit"); _do_effect_if_needed(s,ledger,"reserve_stock")
        c=s.continuation_contract; order=c.get("compensation_order",[])
        obs=[x.get("action") for x in s.pending_obligations if x.get("type")=="compensation"]
        if order==["release_stock","refund"] and set(obs)==set(order):
            for op in order: ledger[op]=ledger.get(op,0)+1; s.event("effect_executed_target",op,count=ledger[op]); s.step(op)
            _resolve_type(s,"compensation")
        else: s.step("compensation_contract_missing")
        s.step("finish"); s.terminated=True; s.outcome="compensated"
    elif wf=="lease_renewal_handoff":
        _do_effect_if_needed(s,ledger,"acquire_lease")
        if _has_obligation(s,"lease_renewal"):
            ledger["renew_lease"]=ledger.get("renew_lease",0)+1; s.event("effect_executed_target","renew_lease",count=ledger["renew_lease"]); s.step("renew_lease"); _resolve_type(s,"lease_renewal")
        else: s.step("lease_obligation_missing")
        s.step("critical_section"); s.step("finish"); s.terminated=True; s.outcome="critical_done"
    elif wf=="mixed_idempotency_effects":
        _do_effect_if_needed(s,ledger,"cache_write"); _do_effect_if_needed(s,ledger,"charge"); s.step("verify"); s.step("finish"); s.terminated=True; s.outcome="verified"
    elif wf=="map_reduce_threshold":
        c=s.continuation_contract
        if c.get("quorum")==3 and _has_obligation(s,"cancel_branch"): _resolve_type(s,"cancel_branch"); s.step("reduce")
        else: s.step("shard_4"); s.step("reduce")
        s.step("finish"); s.terminated=True; s.outcome="reduced"
    else: raise KeyError(wf)
    return s

def static_spec(workflow:str)->dict[str,Any]: return deepcopy(STATIC_SPECS[workflow])
