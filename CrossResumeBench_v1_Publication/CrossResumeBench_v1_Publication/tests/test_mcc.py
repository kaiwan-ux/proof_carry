from crossresumebench.generator import generate_suite
from crossresumebench.baselines import build_transfer,lower_transfer
from crossresumebench.semantics import continue_case
from crossresumebench.evaluator import evaluate
def test_mcc_has_no_native_checkpoint_fields():
    for c in generate_suite()[:5]:
        p=build_transfer('mcc',c); blob=str(p.payload).lower(); assert 'checkpoint_id' not in blob and 'native_snapshot' not in blob and 'flow_id' not in blob
def test_oracle_safe_on_all_cases():
    for c in generate_suite():
        p=build_transfer('oracle',c); s=lower_transfer(p,c); t,l=continue_case(c.family,s,dict(c.source_ledger),oracle=True); assert evaluate(c,t,l).safe_completion==1
