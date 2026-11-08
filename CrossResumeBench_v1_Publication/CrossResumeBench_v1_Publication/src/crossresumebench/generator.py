from __future__ import annotations
import random, hashlib
from .models import RuntimeState, CaseSpec

FAMILIES = [
 "approval_then_effect_timeout","effect_then_reject_branch","two_effects_one_ambiguous",
 "parallel_two_effects_partial","nested_loop_retry_effect","callback_after_commit",
 "compensation_after_partial_parallel","one_to_many_mapping","many_to_one_mapping",
 "approval_inside_parallel","retry_budget_split","branch_join_pending_tool",
]
BOUNDARIES=["mid_node_interrupt","task_completed","method_paused","superstep","pending_request","tool_callback"]

def _receipt(case_id,op):
    return {"operation_id":f"{case_id}:{op}","status":"committed","replay":"forbidden","idempotency_key":f"idem:{case_id}:{op}","source":"certified_sink"}

def _ev(s,typ,step,**kw): s.event(typ,step,**kw)

def _base(case_id,fam,v):
    return RuntimeState(case_id=case_id,workflow=fam,app_state={"variant":v,"amount":100+v,"route":"left"})

def make_case(family:str,variant:int,seed:int)->CaseSpec:
    rng=random.Random(seed + variant*7919 + sum(map(ord,family)))
    cid=f"crb-{family}-v{variant:02d}"
    s=_base(cid,family,variant); ledger={}
    graph={"family":family,"version":1,"nodes":[],"edges":[],"semantic_map":{}}
    tags=[]
    # The histories are intentionally rich enough to reconstruct control semantics.
    # Only true external commit state may remain observationally ambiguous.
    if family=="approval_then_effect_timeout":
        s.step("prepare"); _ev(s,"step_completed","prepare")
        s.pending_obligations=[{"type":"approval","id":"approve-1","blocks":"charge"}]; _ev(s,"approval_requested","approve",request_id="approve-1")
        s.frontier={"next":"charge","blocked_on":"approve-1"}; s.contract={"after_approval":"charge"}
        graph["nodes"]=["prepare","approve","charge","finish"]; tags=["interrupt-vs-separate-gate","post-approval-effect"]
    elif family=="effect_then_reject_branch":
        s.step("prepare"); s.effect_receipts["reserve"]=_receipt(cid,"reserve"); ledger["reserve"]=1; _ev(s,"tool_call_observed","reserve",result="timeout",commit_status="unknown"); s.step("reserve")
        s.decisions["risk"]="reject"; _ev(s,"decision_made","risk_router",key="risk",choice="reject"); s.frontier={"next":"reject_path","branch":"reject"}; s.contract={"branch":"reject","do_not_repeat":["reserve"]}
        graph["nodes"]=["prepare","reserve","risk_router","reject_path","finish"]; tags=["effect-before-branch","router-label-mismatch"]
    elif family=="two_effects_one_ambiguous":
        s.effect_receipts["inventory"]=_receipt(cid,"inventory"); ledger["inventory"]=1; _ev(s,"effect_commit_ack","inventory",status="committed"); s.step("inventory")
        s.effect_receipts["charge"]=_receipt(cid,"charge"); ledger["charge"]=1; _ev(s,"tool_call_observed","charge",result="timeout",commit_status="unknown"); s.step("charge")
        s.frontier={"next":"verify"}; s.contract={"order":["inventory","charge","verify"],"exactly_once":["inventory","charge"]}; graph["nodes"]=["inventory","charge","verify","finish"]; tags=["mixed-effect-observability","ordered-effects"]
    elif family=="parallel_two_effects_partial":
        _ev(s,"fanout_started","fanout",branches=["a","b"]); s.step("fanout")
        s.effect_receipts["a_effect"]=_receipt(cid,"a_effect"); ledger["a_effect"]=1; _ev(s,"tool_call_observed","a_effect",result="timeout",commit_status="unknown"); s.step("a")
        s.pending_obligations=[{"type":"parallel_branch","step":"b"}]; s.frontier={"next":"b","join":"join"}; s.contract={"join":"join","requires":["a","b"],"exactly_once":["a","b"]}; graph["nodes"]=["fanout","a","b","join","finish"]; tags=["partial-superstep","fanout-to-sequential"]
    elif family=="nested_loop_retry_effect":
        s.step("start");
        for i in range(1,3): s.loop_counters["outer"]=i; _ev(s,"loop_iteration_completed","outer",iteration=i); s.step(f"loop_{i}")
        s.retry_counts["tool"]=1; _ev(s,"retry_failed","tool",attempt=1,max_attempts=3)
        s.effect_receipts["tool_effect"]=_receipt(cid,"tool_effect"); ledger["tool_effect"]=1; _ev(s,"tool_call_observed","tool_effect",result="timeout",commit_status="unknown")
        s.pending_obligations=[{"type":"retry","step":"tool","next_attempt":2,"max_attempts":3}]; s.frontier={"next":"reconcile_tool","outer_iteration":3}; s.contract={"effect_commit_satisfies_retry":"tool_effect","loop_limit":3}; graph["nodes"]=["start","loop","tool","finish"]; tags=["framework-retry-vs-explicit-retry","loop-position"]
    elif family=="callback_after_commit":
        s.effect_receipts["submit"]=_receipt(cid,"submit"); ledger["submit"]=1; _ev(s,"tool_call_observed","submit",result="accepted_no_callback",commit_status="unknown"); s.step("submit")
        s.pending_obligations=[{"type":"callback","operation":"submit","callback_id":"cb-1"}]; _ev(s,"callback_pending","wait_callback",callback_id="cb-1",operation="submit"); s.frontier={"next":"wait_callback"}; s.contract={"callback_before":"finish"}; graph["nodes"]=["submit","wait_callback","finish"]; tags=["pending-tool-vs-request","callback-state"]
    elif family=="compensation_after_partial_parallel":
        _ev(s,"fanout_started","fanout",branches=["debit","notify"]); s.step("fanout")
        s.effect_receipts["debit"]=_receipt(cid,"debit"); ledger["debit"]=1; _ev(s,"tool_call_observed","debit",result="timeout",commit_status="unknown"); s.step("debit")
        s.step("notify_failed"); _ev(s,"step_failed","notify",reason="permanent")
        s.pending_obligations=[{"type":"compensation","effect":"debit","action":"refund"}]; _ev(s,"compensation_required","refund",effect="debit")
        s.frontier={"next":"refund"}; s.contract={"compensate":"debit","with":"refund","exactly_once":True}; graph["nodes"]=["fanout","debit","notify","refund","finish"]; tags=["error-handler-vs-explicit-compensation","parallel-partial"]
    elif family=="one_to_many_mapping":
        s.effect_receipts["payment"]=_receipt(cid,"payment"); ledger["payment"]=1; _ev(s,"tool_call_observed","source_atomic_payment",result="timeout",commit_status="unknown",operation="payment",semantic_parts=["authorize","commit"]); s.step("source_atomic_payment")
        s.frontier={"next":"target_verify"}; s.contract={"mapping":{"source_atomic_payment":["target_authorize","target_commit"]},"completed_semantics":["authorize","commit"]}; graph["nodes"]=["source_atomic_payment","target_verify","finish"]; tags=["one-to-many-step-map","mid-node-effect"]
    elif family=="many_to_one_mapping":
        s.step("source_authorize"); _ev(s,"step_completed","source_authorize",semantic="authorize")
        s.effect_receipts["payment"]=_receipt(cid,"payment"); ledger["payment"]=1; _ev(s,"tool_call_observed","source_commit",result="timeout",commit_status="unknown",operation="payment",semantic="commit"); s.step("source_commit")
        s.frontier={"next":"target_combined_after_commit"}; s.contract={"mapping":{"target_combined":["authorize","commit"]},"completed_semantics":["authorize","commit"]}; graph["nodes"]=["source_authorize","source_commit","target_combined","finish"]; tags=["many-to-one-step-map","granularity-mismatch"]
    elif family=="approval_inside_parallel":
        _ev(s,"fanout_started","fanout",branches=["human_branch","auto_branch"]); s.step("fanout"); s.step("auto_branch"); _ev(s,"step_completed","auto_branch")
        s.pending_obligations=[{"type":"approval","id":"parallel-approval","blocks":"human_branch"}]; _ev(s,"approval_requested","human_branch",request_id="parallel-approval")
        s.frontier={"next":"human_branch","join":"join"}; s.contract={"join":"join","requires":["human_branch","auto_branch"]}; graph["nodes"]=["fanout","human_branch","auto_branch","join","finish"]; tags=["hitl-inside-parallel","request-reemission"]
    elif family=="retry_budget_split":
        s.retry_counts["remote_call"]=2; _ev(s,"retry_failed","remote_call",attempt=1,max_attempts=3); _ev(s,"retry_failed","remote_call",attempt=2,max_attempts=3); s.step("attempt_1"); s.step("attempt_2")
        s.pending_obligations=[{"type":"retry","step":"remote_call","next_attempt":3,"max_attempts":3}]; s.frontier={"next":"attempt_3"}; s.contract={"max_attempts":3,"remaining_budget":1}; graph["nodes"]=["remote_call","finish"]; tags=["retry-budget-ownership","native-policy-vs-tool-policy"]
    elif family=="branch_join_pending_tool":
        s.decisions["route"]="left"; _ev(s,"decision_made","router",key="route",choice="left"); s.step("router"); _ev(s,"fanout_started","fanout",branches=["tool","compute"]); s.step("fanout"); s.step("compute"); _ev(s,"step_completed","compute")
        s.effect_receipts["tool"]=_receipt(cid,"tool"); ledger["tool"]=1; _ev(s,"tool_call_observed","tool",result="timeout",commit_status="unknown")
        s.pending_obligations=[{"type":"tool_result","operation":"tool"}]; s.frontier={"next":"reconcile_tool","join":"join","branch":"left"}; s.contract={"join":"join","requires":["tool","compute"],"branch":"left"}; graph["nodes"]=["router","fanout","tool","compute","join","finish"]; tags=["pending-tool-at-join","branch-plus-parallel"]
    else: raise KeyError(family)

    # Add graph edges linearly as a neutral carrier; contracts/history hold non-linear semantics.
    ns=graph["nodes"]; graph["edges"]=[[a,b] for a,b in zip(ns,ns[1:])]
    source_boundary=BOUNDARIES[(variant+len(family))%len(BOUNDARIES)]
    target_boundary=BOUNDARIES[(variant*3+len(family))%len(BOUNDARIES)]
    tags=tags+[f"source:{source_boundary}",f"target:{target_boundary}"]
    # Oracle reference is produced by the same target transition using complete semantics.
    from .semantics import continue_case
    ref_state,ref_ledger=continue_case(family,s.clone(),dict(ledger),oracle=True)
    return CaseSpec(cid,family,variant,graph,s.to_dict(),dict(ledger),ref_state.to_dict(),dict(ref_ledger),tags,source_boundary,target_boundary,{"seed":seed,"generated":True})

def generate_suite(seed:int=260826,variants_per_family:int=5):
    out=[]
    for fam in FAMILIES:
        for v in range(1,variants_per_family+1): out.append(make_case(fam,v,seed))
    return out
