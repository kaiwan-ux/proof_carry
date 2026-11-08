from collections import Counter
from crossresumebench_proofcarry.cases import CASES

def test_120_independent_cases():
    assert len(CASES)==120
    assert len({c.case_id for c in CASES})==120
    counts=Counter(c.family for c in CASES); assert set(counts.values())=={15}; assert len(counts)==8
    assert len({c.scenario_name for c in CASES})==120
