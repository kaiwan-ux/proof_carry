from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def test_suite_shape():
    s=json.loads((ROOT/'studies/security/security_suite.json').read_text())
    assert len(s['cases'])==16 and len(s['runtime_pairs'])==6 and len(s['attack_variants'])==8
def test_figure_script_exists(): assert (ROOT/'figures/scripts/generate_paper_figures.py').exists()
def test_mechanism_frozen_present(): assert (ROOT/'mechanism/MCCV3_MECHANISM_SHA256.txt').exists()
