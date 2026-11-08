from portaflow_holdout.benchmark import SCENARIOS,initial_state,source_prefix_transition,continuation_transition,STATIC_SPECS
from portaflow_holdout.models import SourceCapture,ExecutionState
from portaflow_holdout.capsule import build_capsule,lower_capsule

def source(w):
    ld={}; s=source_prefix_transition(initial_state(w),ld); return SourceCapture('x',w,s.to_dict(),{'kind':'x'},ld)

def run(w,parts,mode):
    src=source(w); cap=build_capsule(src,parts,mode); imp,rep,ok,reason=lower_capsule(cap)
    if not ok:return ok,reason,None
    ld=dict(src.external_ledger); out=continuation_transition(imp,ld); return True,None,(out,ld)

def test_true_holdout_has_ten_new_workflows():
    assert len(SCENARIOS)==10
    old={'branch_effect_approval','loop_effect','parallel_retry_join','retry_effect_uncertain','approval_loop','saga_compensation','nested_parallel_effect','branch_parallel_merge'}
    assert not (set(SCENARIOS)&old)

def test_generic_inference_engine_has_no_workflow_conditionals():
    import inspect,portaflow_holdout.history as h
    txt=inspect.getsource(h.infer_semantics)
    assert 'workflow==' not in txt and 'workflow ==' not in txt

def test_hybrid_frozen_candidate_completes_all_holdouts():
    for w in SCENARIOS:
        ok,reason,res=run(w,('history','receipts'),'hybrid'); assert ok,(w,reason)
        out,ld=res; assert out.terminated

def test_explicit_frozen_candidate_completes_all_holdouts():
    for w in SCENARIOS:
        ok,reason,res=run(w,('frontier','obligations','receipts','contract'),'explicit'); assert ok,(w,reason)
        out,ld=res; assert out.terminated

def test_history_inference_rejects_at_least_one_ambiguous_effect():
    rejected=[]
    for w in SCENARIOS:
        ok,reason,_=run(w,('history',),'hybrid')
        if not ok: rejected.append((w,reason))
    assert rejected and all(r=='AMBIGUOUS_EXTERNAL_COMMIT' for _,r in rejected)

def test_receipts_are_not_native_checkpoint_blobs():
    import json
    c=build_capsule(source(SCENARIOS[0]),('history','receipts'),'hybrid').to_dict(); blob=json.dumps(c)
    for bad in ['\"checkpoint_id\"','\"flow_id\"','\"latest_checkpoint\"','\"native_snapshot\"']:
        assert bad not in blob
