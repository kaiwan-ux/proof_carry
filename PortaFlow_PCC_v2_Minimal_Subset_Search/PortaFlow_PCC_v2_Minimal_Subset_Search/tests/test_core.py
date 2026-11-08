from portaflow_min.components import all_subsets,COMPONENTS
from portaflow_min.search import exhaustive_rows
from portaflow_min.capsule import build_capsule,lower_capsule
from portaflow_min.search import canonical_source


def test_64_subsets():
    ss=list(all_subsets()); assert len(ss)==64; assert tuple() in ss; assert tuple(COMPONENTS) in ss

def test_exhaustive_shape():
    rows=exhaustive_rows(); assert len(rows)==1024

def test_history_only_rejects_ambiguous_commit_safely():
    c=canonical_source('retry_effect_uncertain'); cap=build_capsule(c,['history'],'hybrid'); _,rep,accepted,reason=lower_capsule(cap)
    assert not accepted and reason=='AMBIGUOUS_EXTERNAL_COMMIT' and rep['unresolved_critical_facts']

def test_receipt_resolves_history_ambiguity():
    c=canonical_source('retry_effect_uncertain'); cap=build_capsule(c,['history','receipts'],'hybrid'); _,rep,accepted,reason=lower_capsule(cap)
    assert accepted and reason is None

def test_capsule_has_no_native_blob():
    import json
    c=canonical_source('branch_effect_approval'); cap=build_capsule(c,COMPONENTS,'explicit'); txt=json.dumps(cap.to_dict())
    for key in ['native_snapshot','latest_checkpoint','checkpoint_id','flow_id']: assert f'"{key}"' not in txt
