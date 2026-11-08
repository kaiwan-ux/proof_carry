from __future__ import annotations
import hashlib,json
from pathlib import Path
from crossresumebench_v2.models import CaseSpec

PORTABLE_HISTORY=[
    {"type":"tool_call_observed","step":"effect_attempt","semantic_unit":"effect_attempt","data":{"operation":"effect","commit_status":"unknown","parent_unit":"effect_attempt","unit_completion_observable":True}},
    {"type":"semantic_unit_completed","semantic_unit":"effect_attempt","data":{"unit":"effect_attempt"}},
]

def case_spec():
    return CaseSpec(
        case_id="effect_commit_two_worlds",family="effect_acknowledgment_points",variant=1,
        app_state={"phase":"effect_attempted"},source_actions=[],
        target_actions=[
            {"action_id":"effect_guard","semantic_unit":"effect_guard","kind":"effect","operation":"effect"},
            {"action_id":"ack","semantic_unit":"ack","kind":"step"},
            {"action_id":"finish","semantic_unit":"finish","kind":"finish"},
        ],
        target_dependencies={"ack":["effect_guard"],"finish":["ack"]},
        expected_semantic_units=["effect_attempt","effect_guard","ack","finish"],
        expected_effect_counts={"effect":1},
        mismatch_tags=["two_world_commit_ambiguity","real_native_pause","effect_guard"],
        source_boundary="after_attempt_before_ack",target_boundary="effect_guard_then_ack_finish",
        metadata={"revision":"A","frozen_mcc_v2":True},
    )

def spec_hash():
    b=json.dumps(case_spec().to_dict(),sort_keys=True,separators=(",",":"),default=str).encode()
    return hashlib.sha256(b).hexdigest()
