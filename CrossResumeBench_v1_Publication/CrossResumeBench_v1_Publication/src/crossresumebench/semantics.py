from __future__ import annotations
from .models import RuntimeState

def _committed(s,op): return s.effect_receipts.get(op,{}).get("status")=="committed"
def _has_ob(s,typ,**kw): return any(x.get("type")==typ and all(x.get(k)==v for k,v in kw.items()) for x in s.pending_obligations)
def _effect(s,ledger,op):
    if _committed(s,op):
        # Certified receipt proves the external effect already happened; mark semantic completion without replaying it.
        if op not in s.completed_steps: s.completed_steps.append(op)
        s.event("effect_skipped_by_receipt",op)
        return
    ledger[op]=ledger.get(op,0)+1; s.event("effect_executed_target",op,count=ledger[op]); s.step(op)

def continue_case(fam:str,s:RuntimeState,ledger:dict[str,int],oracle:bool=False):
    # This interpreter is framework-neutral. Native adapters execute this continuation inside each runtime.
    if fam=="approval_then_effect_timeout":
        if _has_ob(s,"approval"):
            s.event("approval_resolved","approve",approved=True); s.pending_obligations=[]
        _effect(s,ledger,"charge"); s.step("finish"); s.outcome="done"
    elif fam=="effect_then_reject_branch":
        _effect(s,ledger,"reserve"); route=s.frontier.get("branch") or s.decisions.get("risk") or "approve"; s.step(f"{route}_path"); s.step("finish"); s.outcome=route
    elif fam=="two_effects_one_ambiguous":
        _effect(s,ledger,"inventory"); _effect(s,ledger,"charge"); s.step("verify"); s.step("finish"); s.outcome="done"
    elif fam=="parallel_two_effects_partial":
        _effect(s,ledger,"a_effect");
        if _has_ob(s,"parallel_branch",step="b") or "a" in s.completed_steps: s.step("b")
        else: s.step("a"); s.step("b")
        s.step("join"); s.step("finish"); s.outcome="done"
    elif fam=="nested_loop_retry_effect":
        _effect(s,ledger,"tool_effect"); start=int(s.frontier.get("outer_iteration",1));
        for i in range(start,4): s.loop_counters["outer"]=i; s.step(f"loop_{i}")
        if s.retry_counts.get("tool",0)<1: s.step("retry_replayed")
        s.step("finish"); s.outcome="done"
    elif fam=="callback_after_commit":
        _effect(s,ledger,"submit")
        if _has_ob(s,"callback",operation="submit"): s.event("callback_received","wait_callback",callback_id="cb-1"); s.pending_obligations=[]
        else: s.step("submit_again_wait")
        s.step("finish"); s.outcome="done"
    elif fam=="compensation_after_partial_parallel":
        _effect(s,ledger,"debit")
        if _has_ob(s,"compensation",effect="debit") or s.contract.get("compensate")=="debit": _effect(s,ledger,"refund"); s.step("refund")
        else: s.step("notify_retry"); _effect(s,ledger,"debit")
        s.step("finish"); s.outcome="compensated" if ledger.get("refund",0)==1 else "unsafe"
    elif fam=="one_to_many_mapping":
        _effect(s,ledger,"payment")
        if "source_atomic_payment" not in s.completed_steps and "commit" not in s.contract.get("completed_semantics",[]): s.step("target_authorize"); s.step("target_commit")
        s.step("target_verify"); s.step("finish"); s.outcome="done"
    elif fam=="many_to_one_mapping":
        _effect(s,ledger,"payment")
        done=set(s.contract.get("completed_semantics",[]))
        if not {"authorize","commit"}.issubset(done) and not {"source_authorize","source_commit"}.issubset(set(s.completed_steps)): s.step("target_combined")
        s.step("finish"); s.outcome="done"
    elif fam=="approval_inside_parallel":
        if _has_ob(s,"approval"):
            s.event("approval_resolved","human_branch",approved=True); s.step("human_branch")
        else: s.step("human_branch_without_gate")
        if "auto_branch" not in s.completed_steps: s.step("auto_branch")
        s.step("join"); s.step("finish"); s.outcome="done"
    elif fam=="retry_budget_split":
        attempt=s.retry_counts.get("remote_call",0)+1
        if attempt!=3: s.step(f"wrong_attempt_{attempt}")
        s.retry_counts["remote_call"]=attempt; s.step(f"attempt_{attempt}"); s.step("finish"); s.outcome="done" if attempt==3 else "wrong_retry_budget"
    elif fam=="branch_join_pending_tool":
        _effect(s,ledger,"tool"); branch=s.frontier.get("branch") or s.decisions.get("route") or "right"
        if branch!="left": s.step("right_branch")
        if "compute" not in s.completed_steps: s.step("compute")
        s.step("join"); s.step("finish"); s.outcome="done" if branch=="left" else "wrong_branch"
    else: raise KeyError(fam)
    s.terminated=True
    return s,ledger
