from portaflow_phase0.workflows import run_prefix, spec


def test_prefix_boundaries():
    for name in ("linear","branch","loop","retry","approval","side_effect"):
        s=run_prefix(name,0)
        assert s.current_step==spec(name).boundary
        assert not s.terminated


def test_side_effect_prefix_committed_once():
    s=run_prefix("side_effect",0)
    assert s.effects["mock_payment"]==1
