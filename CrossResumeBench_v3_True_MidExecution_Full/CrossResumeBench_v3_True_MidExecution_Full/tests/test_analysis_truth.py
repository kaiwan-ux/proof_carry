from crossresumebench_v3_full.cases import CASES
def test_every_case_has_enough(): assert all("enough_evidence" in c.applicable_variants for c in CASES)
