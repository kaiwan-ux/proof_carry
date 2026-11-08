from portaflow_v1.benchmark import SCENARIOS,initial_state,source_prefix_transition,continuation_transition,static_spec
from portaflow_v1.models import SourceCapture
from portaflow_v1.pcc import CONDITIONS,build_capsule,lower_capsule
from portaflow_v1.history import infer_semantics

OLD={"retry","approval","side_effect","branch","loop","parallel"}

def fake_capture(wf):
    ld={}; s=source_prefix_transition(initial_state(wf),ld)
    return SourceCapture("fake",wf,s.to_dict(),{"kind":"fake_native"},ld)

def test_holdout_names_are_new():
    assert not (set(SCENARIOS)&OLD)
    assert len(SCENARIOS)==8

def test_full_pcc_never_contains_native_snapshot():
    c=fake_capture(SCENARIOS[0]); cap=build_capsule(c,"full_pcc_v1").to_dict(); text=str(cap)
    assert "latest_checkpoint" not in text and "checkpoint_id" not in text and "flow_id" not in text

def test_history_is_not_redacted():
    c=fake_capture("branch_effect_approval"); cap=build_capsule(c,"raw_history")
    assert any(e["kind"]=="decision_made" and e["detail"].get("choice")=="left" for e in cap.semantic_history)
    assert any(e["kind"]=="tool_call_observed" and e["detail"].get("commit_status")=="unknown" for e in cap.semantic_history)

def test_inference_can_reconstruct_obvious_fields():
    c=fake_capture("approval_loop"); cap=build_capsule(c,"history_inference"); s,rep,ok,reason=lower_capsule(cap)
    assert ok and reason is None
    assert s.control_frontier.get("iteration")==3
    assert any(x.get("type")=="human_approval" for x in s.pending_obligations)

def test_inference_rejects_unknown_external_commit():
    c=fake_capture("retry_effect_uncertain"); cap=build_capsule(c,"history_inference"); s,rep,ok,reason=lower_capsule(cap)
    assert not ok and reason=="AMBIGUOUS_EXTERNAL_COMMIT"

def test_full_pcc_completes_all_holdouts_with_logical_executor():
    for wf in SCENARIOS:
        c=fake_capture(wf); cap=build_capsule(c,"full_pcc_v1"); s,rep,ok,reason=lower_capsule(cap); assert ok
        ld=dict(c.external_ledger); out=continuation_transition(s,ld)
        assert out.terminated
