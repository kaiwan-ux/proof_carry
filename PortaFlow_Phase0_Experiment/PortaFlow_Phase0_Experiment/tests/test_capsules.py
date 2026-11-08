from portaflow_phase0.baselines import export_capsule, import_capsule
from portaflow_phase0.workflows import run_prefix


def test_naive_omits_execution_obligations():
    s=run_prefix("approval",0)
    c=export_capsule(s,"naive_state")
    assert "pending_approval" not in c.payload


def test_history_masks_effect_commitment_status():
    s=run_prefix("side_effect",0)
    c=export_capsule(s,"state_history")
    restored=import_capsule(c)
    assert restored.effects.get("mock_payment") is None
    assert any(e.kind == "tool_call_observed" for e in restored.trace)


def test_oracle_round_trip():
    s=run_prefix("retry",0)
    restored=import_capsule(export_capsule(s,"oracle_full"))
    assert restored.retry_attempts==1
    assert restored.completed==s.completed
