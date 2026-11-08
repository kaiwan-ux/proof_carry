from collections import Counter
from crossresumebench_proofcarry.cases import CASES

def test_104_independent_cases():
    assert len(CASES)==104
    assert len({c.case_id for c in CASES})==104
    counts=Counter(c.family for c in CASES); assert set(counts.values())=={13}; assert len(counts)==8
    assert len({c.scenario_name for c in CASES})==104
