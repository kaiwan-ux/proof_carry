from pathlib import Path

def test_no_truth_import():
    root=Path(__file__).resolve().parents[1]
    t=(root/'mechanism/mcc_v3.py').read_text()
    forbidden_imports=['from crossresumebench_mccv3.cases','import crossresumebench_mccv3.cases','from crossresumebench_mccv3.semantics','import crossresumebench_mccv3.semantics']
    assert not any(x in t for x in forbidden_imports)
    # Forbidden payload field names are intentionally present only in the defensive scanner.
    assert 'capture["truth_facts"]' not in t and "capture['truth_facts']" not in t
    assert 'capture["oracle_plan"]' not in t and "capture['oracle_plan']" not in t
