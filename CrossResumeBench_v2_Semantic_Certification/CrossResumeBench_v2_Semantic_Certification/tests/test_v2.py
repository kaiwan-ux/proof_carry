from pathlib import Path
import json
from crossresumebench_v2.generator import generate_suite
from crossresumebench_v2.source_engine import simulate_source
from crossresumebench_v2.baselines.core import build_transfer,lower_transfer
from crossresumebench_v2.mcc import validate_mcc_payload
from crossresumebench_v2.target_engine import execute_target
from crossresumebench_v2.evaluator import evaluate
ROOT=Path(__file__).resolve().parents[1]

def test_suite_is_new_and_size():
    cases=generate_suite(); assert len(cases)==70; assert len({c.family for c in cases})==14; assert not any(c.family=='parallel_two_effects_partial' for c in cases)

def test_mcc_schema_has_no_state():
    c=generate_suite()[0]; cap=simulate_source(c); p=build_transfer('mcc_v2',cap,c,'crewai',ROOT); validate_mcc_payload(p.payload,ROOT); assert 'state' not in p.payload and 'frontier' not in p.payload

def test_schema_rejects_hidden_state():
    c=generate_suite()[0]; cap=simulate_source(c); p=build_transfer('mcc_v2',cap,c,'maf',ROOT); p.payload['state']={}
    import pytest
    with pytest.raises(Exception): validate_mcc_payload(p.payload,ROOT)

def test_completion_certificate_fixes_parent_gap():
    c=[x for x in generate_suite() if x.family=='effect_parent_completion_gap'][0]; cap=simulate_source(c); p=build_transfer('mcc_v2',cap,c,'semantic',ROOT); rc=lower_transfer(p,cap,c,ROOT); assert p.accepted; assert 'purchase' in rc.completed_units; t=execute_target(c,rc,dict(cap.source_ledger)); ev=evaluate(c,cap,t); assert ev.safe_completion==1

def test_missing_completion_certificate_rejects_not_replays():
    c=[x for x in generate_suite() if x.family=='effect_parent_completion_gap'][0]; cap=simulate_source(c); cap.certificates=[x for x in cap.certificates if x['fact_type']!='semantic_completion']; p=build_transfer('mcc_v2',cap,c,'semantic',ROOT); rc=lower_transfer(p,cap,c,ROOT); assert not p.accepted; assert 'AMBIGUOUS_SEMANTIC_COMPLETION' in p.reject_reason

def test_baselines_independent_modules():
    from crossresumebench_v2.baselines import history_baseline,aaif_reference,caplease_reference
    import inspect
    assert 'reconstruct_mcc_v2' not in inspect.getsource(history_baseline)
    assert 'reconstruct_mcc_v2' not in inspect.getsource(aaif_reference)
    assert 'reconstruct_mcc_v2' not in inspect.getsource(caplease_reference)

def test_mcc_all_cases_produce_well_formed_decisions():
    # The benchmark is allowed to falsify MCC; this test checks only that every case yields a deterministic decision/result.
    for c in generate_suite():
        cap=simulate_source(c); p=build_transfer('mcc_v2',cap,c,'semantic',ROOT); rc=lower_transfer(p,cap,c,ROOT)
        if not p.accepted:
            assert p.reject_reason
            continue
        ev=evaluate(c,cap,execute_target(c,rc,dict(cap.source_ledger)))
        assert ev.safe_completion + ev.safe_rejection + ev.unsafe_violation == 1

def test_variants_change_evidence_not_only_labels():
    cs=[c for c in generate_suite() if c.family=='effect_parent_completion_gap']
    caps=[simulate_source(c) for c in cs]
    signatures=[]
    for cap in caps:
        signatures.append((tuple((e['type'],e.get('data',{}).get('commit_status')) for e in cap.portable_history),
                           tuple((c['fact_type'],c['subject']) for c in cap.certificates)))
    assert len(set(signatures)) >= 4

def test_native_runner_invokes_source_adapter(tmp_path):
    from crossresumebench_v2.native_runner import run_native
    from crossresumebench_v2.adapters.fake_adapter import FakeAdapter
    calls=[]
    class Counting(FakeAdapter):
        def capture_source(self,case):
            calls.append((self.name,case.case_id)); return super().capture_source(case)
    c=generate_suite()[0]
    rows=run_native([c],['srcA','srcB'],['state_only'],tmp_path,adapter_getter=lambda n: Counting(n))
    assert len(rows)==2
    assert sorted(x[0] for x in calls)==['srcA','srcB']
