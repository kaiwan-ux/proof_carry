from pathlib import Path
from studies.common import verify_passed_holdout_inputs, ROOT
from studies.ablation.ablation_engine import ABLATIONS
from crossresumebench_mccv3.cases import CASES

def test_input_integrity(): assert verify_passed_holdout_inputs()['verified']
def test_holdout_shape_unchanged(): assert len(CASES)==32 and sum(len(c.variants) for c in CASES)==128
def test_ablation_count(): assert len(ABLATIONS)==7 and 'full_mcc_v3' in ABLATIONS
def test_mechanism_freeze_files_present():
    assert (ROOT/'mechanism/MCCV3_MECHANISM_SHA256.txt').exists()
    assert (ROOT/'benchmark/HOLDOUT_SEAL.json').exists()
