from portaflow_pcc.models import LogicalState, SourceCapture
from portaflow_pcc.scenarios import source_prefix_transition, continuation_transition
from portaflow_pcc.pcc import build_capsule, lower_capsule, CONDITIONS
from portaflow_pcc.evaluator import evaluate


def capture(workflow):
    s=LogicalState(workflow=workflow,request_id=f'pcc-{workflow}-001'); ledger={}
    out=source_prefix_transition(s,ledger)
    return SourceCapture('fake',workflow,out.to_dict(),{'kind':'fake_native','secret':'must_not_transfer'},ledger)


def run_case(workflow,condition):
    cap=capture(workflow); source=LogicalState.from_dict(cap.state); ledger=dict(cap.external_ledger)
    c=build_capsule(cap,condition)
    assert 'secret' not in str(c.to_dict())
    imported=lower_capsule(c); target=continuation_transition(imported,ledger)
    return evaluate(source,target,ledger),c


def test_expected_cumulative_ablation():
    expected={
        'state_only': set(),
        'state_history': {'retry'},
        'plus_control_frontier': {'retry','branch','loop'},
        'plus_pending_obligations': {'retry','branch','loop','approval'},
        'plus_effect_receipts': {'retry','branch','loop','approval','side_effect'},
        'full_pcc_v0': {'retry','branch','loop','approval','side_effect','parallel'},
    }
    workflows=['retry','approval','side_effect','branch','loop','parallel']
    for cond in CONDITIONS:
        safe={wf for wf in workflows if run_case(wf,cond)[0]['safe']}
        assert safe==expected[cond], (cond,safe)


def test_capsule_sections_are_cumulative():
    cap=capture('parallel')
    expected=[0,1,2,3,4,5]
    counts=[]
    for c in CONDITIONS:
        d=build_capsule(cap,c).to_dict()
        fields=['semantic_history','control_frontier','pending_obligations','effect_receipts','continuation_contract']
        counts.append(sum(d[f] is not None for f in fields))
    assert counts==expected


def test_wire_size_is_non_decreasing_for_cumulative_ablation():
    cap=capture('parallel')
    sizes=[build_capsule(cap,c).byte_size() for c in CONDITIONS]
    assert sizes==sorted(sizes), sizes

def test_full_pcc_has_no_native_blob():
    c=build_capsule(capture('side_effect'),'full_pcc_v0').to_dict()
    text=str(c)
    assert 'source_native_snapshot' not in text
    assert 'must_not_transfer' not in text
