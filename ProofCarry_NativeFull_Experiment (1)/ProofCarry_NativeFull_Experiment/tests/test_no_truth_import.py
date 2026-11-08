from pathlib import Path

def test_mechanism_does_not_import_case_truth():
    root=Path(__file__).resolve().parents[1]; txt=(root/'mechanism'/'proofcarry.py').read_text().lower(); forbidden=['truth_facts','oracle_plan','crossresumebench_proofcarry.cases']; assert not any(x in txt for x in forbidden)
