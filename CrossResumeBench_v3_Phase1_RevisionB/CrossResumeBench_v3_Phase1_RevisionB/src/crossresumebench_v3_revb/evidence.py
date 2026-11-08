from __future__ import annotations
from .frozen import SourceCapture
from .case import PORTABLE_HISTORY
from crossresumebench_v2.certificates import issue_certificate

VALID_WORLDS={"committed","not_committed"}
VALID_VARIANTS={"enough_evidence","ambiguous_external_commit"}

def source_capture_from_native(native,variant:str):
    if native.world not in VALID_WORLDS: raise ValueError(native.world)
    if variant not in VALID_VARIANTS: raise ValueError(variant)
    certs=[]
    if variant=="enough_evidence":
        certs.append(issue_certificate(
            native.case_id,"effect_commitment","effect",native.world,native.case_id,
            {"idempotency_key":"revb-effect-001","native_checkpoint_ref":native.checkpoint_ref},
        ).to_dict())
    # IMPORTANT: app_state + history are deliberately identical across committed/not_committed worlds.
    obs=dict(native.native_observation); obs["framework"]=native.framework
    return SourceCapture(
        case_id=native.case_id,workflow="phase1_revb_effect_ack",
        app_state={"phase":"effect_attempted"},portable_history=[dict(x) for x in PORTABLE_HISTORY],
        certificates=certs,source_ledger={"effect":native.source_ledger["effect_count"]},native_observation=obs,
        truth_completed_units=["effect_attempt"],truth_pending_obligations=[{"type":"ack"}],
        truth_dependencies={"ack":["effect_guard"],"finish":["ack"]},
    )
