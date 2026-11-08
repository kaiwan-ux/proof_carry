from portaflow_robust.benchmark import SCENARIOS,BASE_WORKFLOWS,PROFILES,initial_state,source_prefix_transition,continuation_transition,static_spec,split_case
from portaflow_robust.models import SourceCapture
from portaflow_robust.capsule import build_capsule,lower_capsule

def source(c):
    ld={};s=source_prefix_transition(initial_state(c),ld);return SourceCapture('x',c,s.to_dict(),{'kind':'x'},ld)
def lower(c,parts,mode):return lower_capsule(build_capsule(source(c),parts,mode))

def test_matrix_has_40_pre_registered_cases():assert len(BASE_WORKFLOWS)==8 and len(PROFILES)==5 and len(SCENARIOS)==40

def test_generic_inference_no_workflow_name_rules():
    import inspect,portaflow_robust.history as h
    t=inspect.getsource(h.infer_semantics);assert 'workflow==' not in t and 'workflow ==' not in t

def test_hybrid_survives_noise_and_order_perturbations():
    for base in BASE_WORKFLOWS:
        for prof in ['baseline','noise_duplicate','out_of_order']:
            c=f'{base}::{prof}';s=source(c);imp,rep,ok,reason=lower(c,('history','receipts'),'hybrid');assert ok,(c,reason);ld=dict(s.external_ledger);out=continuation_transition(imp,ld);assert out.terminated

def test_explicit_survives_partial_history_loss():
    for base in BASE_WORKFLOWS:
        c=f'{base}::partial_history_loss';imp,rep,ok,reason=lower(c,('frontier','obligations','receipts','contract'),'explicit');assert ok,(c,reason)

def test_history_loss_fails_closed_for_at_least_one_case():
    rs=[]
    for base in BASE_WORKFLOWS:
        c=f'{base}::partial_history_loss';_,_,ok,reason=lower(c,('history',),'hybrid');
        if not ok:rs.append(reason)
    assert rs and all(r in {'INSUFFICIENT_CONTINUATION_EVIDENCE','AMBIGUOUS_EXTERNAL_COMMIT'} for r in rs)

def test_receipt_conflict_detected_when_history_and_receipt_are_both_present():
    found=0
    for base in BASE_WORKFLOWS:
        c=f'{base}::receipt_conflict';_,_,ok,reason=lower(c,('history','receipts'),'hybrid')
        if reason=='CONFLICTING_EFFECT_EVIDENCE':found+=1
    assert found>=3

def test_explicit_receipt_only_cannot_detect_all_conflicts():
    # This is a deliberate robustness risk: explicit capsules need authenticated/verifiable receipts.
    accepted=0
    for base in BASE_WORKFLOWS:
        c=f'{base}::receipt_conflict';_,_,ok,reason=lower(c,('frontier','obligations','receipts','contract'),'explicit')
        accepted += int(ok)
    assert accepted>=1

def test_no_native_checkpoint_leak():
    import json
    c=SCENARIOS[0];blob=json.dumps(build_capsule(source(c),('history','receipts'),'hybrid').to_dict())
    for bad in ['"checkpoint_id"','"flow_id"','"latest_checkpoint"','"native_snapshot"']:assert bad not in blob
