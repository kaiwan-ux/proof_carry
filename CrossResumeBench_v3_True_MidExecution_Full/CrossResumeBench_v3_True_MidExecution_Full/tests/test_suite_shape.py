from crossresumebench_v3_full.cases import CASES
from crossresumebench_v3_full.baselines import METHODS
def test_shape():
    assert len(CASES)==28
    assert {c.family for c in CASES}=={"effect_commitment","retry_pause","approval_wait","parallel_join","loop_pause","compensation_pending","async_callback"}
    assert sum(len(c.applicable_variants) for c in CASES)==80
    assert sum(len(c.applicable_variants) for c in CASES)*6*len(METHODS)==3360
