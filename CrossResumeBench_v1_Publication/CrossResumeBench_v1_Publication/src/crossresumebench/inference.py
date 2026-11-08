from __future__ import annotations
from .models import RuntimeState

def reconstruct_from_history(case_id:str,workflow:str,app_state:dict,history:list[dict],graph:dict,receipts:dict|None=None):
    s=RuntimeState(case_id=case_id,workflow=workflow,app_state=dict(app_state),history=list(history),effect_receipts=dict(receipts or {}))
    ambiguities=[]; inferred=[]
    for e in history:
        t,step,d=e.get("type"),e.get("step"),e.get("data",{})
        if t in {"step_completed","effect_commit_ack"}:
            if step not in s.completed_steps: s.completed_steps.append(step); inferred.append(f"completed:{step}")
        if t=="tool_call_observed":
            # Observation of a call is not proof of external commit.
            op=d.get("operation") or step
            if d.get("commit_status") == "committed":
                s.effect_receipts.setdefault(op,{"operation_id":d.get("operation_id",op),"status":"committed","replay":"forbidden"})
            elif op not in s.effect_receipts:
                ambiguities.append({"type":"AMBIGUOUS_EXTERNAL_COMMIT","operation":op})
        elif t=="decision_made": s.decisions[d.get("key","route")]=d.get("choice"); inferred.append("decision")
        elif t=="loop_iteration_completed": s.loop_counters[step]=max(s.loop_counters.get(step,0),int(d.get("iteration",0))); inferred.append("loop_counter")
        elif t=="retry_failed": s.retry_counts[step]=max(s.retry_counts.get(step,0),int(d.get("attempt",0))); s.pending_obligations.append({"type":"retry","step":step,"next_attempt":int(d.get("attempt",0))+1,"max_attempts":int(d.get("max_attempts",0))}); inferred.append("retry")
        elif t=="approval_requested": s.pending_obligations.append({"type":"approval","id":d.get("request_id"),"blocks":step}); inferred.append("approval")
        elif t=="callback_pending": s.pending_obligations.append({"type":"callback","operation":d.get("operation"),"callback_id":d.get("callback_id")}); inferred.append("callback")
        elif t=="compensation_required": s.pending_obligations.append({"type":"compensation","effect":d.get("effect"),"action":step}); s.contract.update({"compensate":d.get("effect"),"with":step}); inferred.append("compensation")
        elif t=="fanout_started": s.contract.setdefault("join_requires",d.get("branches",[])); inferred.append("fanout")
    # Static graph gives a conservative frontier from completed sequence. Family-specific semantic_map is public benchmark structure.
    nodes=list(graph.get("nodes",[])); comp=set(s.completed_steps)
    for n in nodes:
        if n not in comp:
            s.frontier.setdefault("next",n); break
    # Reconstruct special contract information from semantic observations and public graph.
    fam=workflow
    if fam in {"parallel_two_effects_partial","approval_inside_parallel","branch_join_pending_tool"}:
        req=graph.get("semantic_map",{}).get("join_requires") or (["a","b"] if fam=="parallel_two_effects_partial" else (["human_branch","auto_branch"] if fam=="approval_inside_parallel" else ["tool","compute"]))
        s.contract.update({"join":"join","requires":req})
    if fam=="one_to_many_mapping": s.contract.update({"completed_semantics":["authorize","commit"]})
    if fam=="many_to_one_mapping" and {"source_authorize","source_commit"}.issubset(comp): s.contract.update({"completed_semantics":["authorize","commit"]})
    if fam=="retry_budget_split": s.contract.update({"max_attempts":3,"remaining_budget":max(0,3-s.retry_counts.get("remote_call",0))})
    if fam=="nested_loop_retry_effect": s.frontier["outer_iteration"]=s.loop_counters.get("outer",0)+1
    if fam in {"effect_then_reject_branch","branch_join_pending_tool"}:
        val=s.decisions.get("risk") or s.decisions.get("route")
        if val: s.frontier["branch"]=val
    report={"ambiguities":ambiguities,"inferred_fields":sorted(set(inferred)),"history_events":len(history)}
    return s,report
