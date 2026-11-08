from crossresumebench_mccv3.cases import CASES
def test_shape(): assert len(CASES)==32 and sum(len(c.variants) for c in CASES)==128 and any(c.family=='composite' for c in CASES)
