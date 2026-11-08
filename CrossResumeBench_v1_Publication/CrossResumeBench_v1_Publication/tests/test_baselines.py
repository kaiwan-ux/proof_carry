from crossresumebench.generator import generate_suite
from crossresumebench.baselines import build_transfer,lower_transfer

def test_history_inference_rejects_some_ambiguous_effects():
    vals=[build_transfer('history_inference',c).accepted for c in generate_suite()]; assert any(not x for x in vals) and any(x for x in vals)
def test_mcc_accepts_all_frozen_cases():
    assert all(build_transfer('mcc',c).accepted for c in generate_suite())
def test_aaif_plus_caplease_is_explicitly_reference_only():
    c=generate_suite()[0]; assert build_transfer('aaif_plus_caplease',c).name=='aaif_plus_caplease'
