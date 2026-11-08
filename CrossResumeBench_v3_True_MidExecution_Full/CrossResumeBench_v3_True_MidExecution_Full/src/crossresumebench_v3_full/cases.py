from __future__ import annotations
import json, hashlib
from pathlib import Path
from .models import FullCase

EFFECT_V=["enough_evidence","ambiguous_external_commit"]
RETRY_V=["enough_evidence","partially_observable_progress","conflicting_granularity"]
APPROVAL_V=["enough_evidence","partially_observable_progress"]
PARALLEL_V=["enough_evidence","missing_semantic_completion","partially_observable_progress","conflicting_granularity"]
LOOP_V=["enough_evidence","partially_observable_progress","conflicting_granularity"]
COMP_V=["enough_evidence","ambiguous_external_commit","partially_observable_progress"]
CALLBACK_V=["enough_evidence","partially_observable_progress","conflicting_granularity"]

def build_cases():
    out=[]
    def add(family,desc,params,variants):
        i=1+sum(1 for c in out if c.family==family)
        out.append(FullCase(f"crb3-{family}-c{i:02d}",family,desc,i,params,list(variants)))
    # 1) Effect commitment / acknowledgement. Alternate ground-truth states.
    for op,status,label in [
        ("payment_post","committed","HTTP POST committed, ack pending"),
        ("db_write","not_committed","DB write not committed, ack pending"),
        ("message_publish","committed","Message publish committed, ack pending"),
        ("tool_side_effect","not_committed","Tool side effect not committed, ack pending"),
    ]: add("effect_commitment",label,{"operation":op,"effect_status":status},EFFECT_V)
    # 2) Retry continuation.
    for cur,mx,label in [(1,3,"after first failure"),(2,4,"after second failure"),(4,5,"near exhaustion"),(3,3,"retry budget exhausted")]:
        add("retry_pause",label,{"unit":"retry_task","current_attempt":cur,"max_attempts":mx},RETRY_V)
    # 3) Approval wait.
    for rid,label in [("approve_release","single approval"),("approve_with_context","approval with context"),("approve_stage_2","second approval"),("approve_sensitive_action","sensitive action approval")]:
        add("approval_wait",label,{"request_id":rid,"approval_unit":"approval_gate"},APPROVAL_V)
    # 4) Parallel completion sets.
    pars=[
        (["branch_a","branch_b"],["branch_a"],"two branches, one completed"),
        (["branch_a","branch_b","branch_c"],["branch_a"],"three branches, one completed"),
        (["branch_a","branch_b","branch_c"],["branch_a","branch_b"],"three branches, two completed"),
        (["branch_a","branch_b","branch_c"],["branch_a","branch_b","branch_c"],"all branches complete, join pending"),
    ]
    for branches,done,label in pars:
        add("parallel_join",label,{"branches":branches,"completed":done,"join":"join","certified_branch":done[-1]},PARALLEL_V)
    # 5) Loop continuation.
    loops=[(2,5,False,"mid loop 2/5"),(3,6,False,"mid loop 3/6"),(4,10,True,"break condition already met"),(2,4,False,"nested-inner equivalent 2/4")]
    for cur,total,br,label in loops: add("loop_pause",label,{"counter_key":"loop:main","current":cur,"total":total,"break":br},LOOP_V)
    # 6) Compensation pending.
    comps=[
        ("payment","refund_payment","committed","refund pending"),
        ("reservation","release_reservation","committed","release pending"),
        ("notification","retract_notification","not_committed","effect absent; compensation should be skipped"),
        ("inventory","restore_inventory","committed","inventory rollback pending"),
    ]
    for op,ca,status,label in comps: add("compensation_pending",label,{"operation":op,"compensation":ca,"effect_status":status},COMP_V)
    # 7) Async callbacks.
    callbacks=[
        ("tool_callback","tool_result","tool result pending"),
        ("webhook_callback","webhook","webhook callback pending"),
        ("subtask_callback","async_subtask","async subtask completion pending"),
        ("timeout_race_callback","timeout_race","callback vs timeout race pending"),
    ]
    for cid,op,label in callbacks: add("async_callback",label,{"callback_id":cid,"operation":op,"callback_unit":"callback_unit"},CALLBACK_V)
    assert len(out)==28
    return out

CASES=build_cases()
CASE_BY_ID={c.case_id:c for c in CASES}

def suite_dict():
    return {"benchmark":"CrossResumeBench_v3_True_MidExecution_Full","cases":[c.to_dict() for c in CASES]}

def suite_hash():
    body=json.dumps(suite_dict(),sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    return hashlib.sha256(body).hexdigest()
