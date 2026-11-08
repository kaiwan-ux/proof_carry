from __future__ import annotations
import hashlib, json
from .frozen import CaseSpec

def case_spec():
    return CaseSpec(
        case_id="effect_committed_ack_pending", family="effect_acknowledgment_points", variant=1,
        app_state={"workflow":"phase1_effect_ack"},
        source_actions=[],
        target_actions=[
            {"action_id":"ack","semantic_unit":"ack","kind":"step"},
            {"action_id":"finish","semantic_unit":"finish","kind":"finish"},
        ],
        target_dependencies={"finish":["ack"]},
        expected_semantic_units=["commit_effect","ack","finish"],
        expected_effect_counts={"effect":1},
        mismatch_tags=["effect_committed_ack_pending","cross_runtime_checkpoint"],
        source_boundary="after_effect_before_ack", target_boundary="ack_then_finish",
        metadata={"phase1":True},
    )

def spec_hash():
    b=json.dumps(case_spec().to_dict(),sort_keys=True,separators=(",",":"),default=str).encode()
    return hashlib.sha256(b).hexdigest()
