from __future__ import annotations
from .frozen import SourceCapture, ROOT
from crossresumebench_v2.certificates import issue_certificate

def source_capture_from_native(native, variant:str):
    history=[
        {"type":"tool_call_observed","step":"commit_effect","semantic_unit":"commit_effect","data":{"operation":"effect","commit_status":"unknown","parent_unit":"commit_effect","unit_completion_observable":False}},
    ]
    certs=[]
    if variant=="enough_evidence":
        certs.append(issue_certificate(native.case_id,"effect_commitment","effect","committed",native.case_id,{"idempotency_key":"phase1-effect","native_checkpoint_ref":native.checkpoint_ref}).to_dict())
        certs.append(issue_certificate(native.case_id,"semantic_completion","commit_effect","completed",native.case_id,{"checkpoint_ref":native.checkpoint_ref}).to_dict())
    elif variant!="ambiguous_external_commit":
        raise ValueError(f"unsupported Phase-1 variant {variant}")
    return SourceCapture(
        case_id=native.case_id, workflow="phase1_effect_ack", app_state=dict(native.app_state), portable_history=history,
        certificates=certs, source_ledger={"effect":native.effect_count}, native_observation=dict(native.native_observation),
        truth_completed_units=["commit_effect"], truth_pending_obligations=[{"type":"ack"}], truth_dependencies={"finish":["ack"]}
    )
