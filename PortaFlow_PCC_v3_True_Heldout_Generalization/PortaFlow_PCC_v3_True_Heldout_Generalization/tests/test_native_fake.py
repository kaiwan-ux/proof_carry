from pathlib import Path
import json
from portaflow_holdout.benchmark import initial_state,source_prefix_transition,continuation_transition
from portaflow_holdout.models import SourceCapture
from portaflow_holdout.native import run_native
from portaflow_holdout.conditions import FROZEN_CONDITIONS
class A:
    def __init__(self,n): self.n=n
    def run_source(self,w):
        ld={}; s=source_prefix_transition(initial_state(w),ld); return SourceCapture(self.n,w,s.to_dict(),{'kind':self.n+'_fake'},ld)
    def run_target(self,w,imp,ld): return continuation_transition(imp,ld),{'kind':self.n+'_fake_target'}
def test_fake_native_matrix(tmp_path:Path):
    from portaflow_holdout.benchmark import SCENARIOS
    cfg={'experiment_name':'t','frameworks':['langgraph','crewai','maf'],'workflows':SCENARIOS}
    rows=run_native(cfg,tmp_path,FROZEN_CONDITIONS,adapter_getter=lambda n:A(n))
    assert len(rows)==10*6*8
    for name in ['hybrid_minimal','explicit_minimal','full_pcc']:
        q=[r for r in rows if r.condition==name]; assert all(r.safe_completion==1 and r.unsafe_violation==0 for r in q)
