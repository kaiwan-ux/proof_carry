from __future__ import annotations
from ..models import ReconstructedContinuation

def infer_history_only(capture,case):
    rc=ReconstructedContinuation(capture.case_id,capture.workflow,dict(capture.app_state)); ambiguous=[]
    for e in capture.portable_history:
        typ=e.get("type"); u=e.get("semantic_unit"); d=e.get("data",{})
        if typ=="semantic_unit_completed" and u and u not in rc.completed_units: rc.completed_units.append(u)
        elif typ=="tool_call_observed":
            op=d.get("operation") or e.get("step")
            if d.get("commit_status")=="committed": rc.effect_facts[op]={"status":"committed","source":"history"}
            elif d.get("commit_status")=="not_committed": rc.effect_facts[op]={"status":"not_committed","source":"history"}
            else: ambiguous.append({"type":"AMBIGUOUS_EXTERNAL_COMMIT","operation":op})
            if d.get("parent_unit") and not d.get("unit_completion_observable",False) and u not in rc.completed_units:
                ambiguous.append({"type":"AMBIGUOUS_SEMANTIC_COMPLETION","semantic_unit":u})
        elif typ=="approval_requested": rc.pending_obligations.append({"type":"approval","id":d.get("request_id"),"blocks":d.get("blocks")})
        elif typ=="callback_pending": rc.pending_obligations.append({"type":"callback","id":d.get("callback_id"),"operation":d.get("operation")})
        elif typ=="compensation_required": rc.pending_obligations.append({"type":"compensation","action":d.get("compensation_action") or u,"effect":d.get("effect")})
        elif typ=="decision_made": rc.decisions[d.get("key")]=d.get("choice")
        elif typ=="counter_observed": rc.counters[d.get("key")]=int(d.get("value",0))
        elif typ=="join_observed" and u: rc.dependencies[u]=list(d.get("requires",[]))
    for k,v in case.target_dependencies.items(): rc.dependencies.setdefault(k,list(v))
    rc.ambiguities=ambiguous
    return rc,{"ambiguities":ambiguous,"implementation":"independent_history_baseline"}
