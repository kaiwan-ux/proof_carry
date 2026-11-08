from pathlib import Path
from portaflow_robust.benchmark import SCENARIOS,initial_state,source_prefix_transition,continuation_transition
from portaflow_robust.models import SourceCapture
from portaflow_robust.native import run_native
from portaflow_robust.conditions import FROZEN_CONDITIONS
class A:
 def __init__(self,n):self.n=n
 def run_source(self,w):
  ld={};s=source_prefix_transition(initial_state(w),ld);return SourceCapture(self.n,w,s.to_dict(),{'kind':self.n+'_fake'},ld)
 def run_target(self,w,imp,ld):return continuation_transition(imp,ld),{'kind':self.n+'_fake_target'}
def test_fake_native_matrix(tmp_path:Path):
 cfg={'experiment_name':'t','frameworks':['langgraph','crewai','maf'],'workflows':SCENARIOS};rows=run_native(cfg,tmp_path,FROZEN_CONDITIONS,adapter_getter=lambda n:A(n));assert len(rows)==40*6*5
 # Hybrid/full can cross-check receipts against history and must fail closed.
 for name in ['hybrid_minimal','full_pcc']:
  q=[r for r in rows if r.condition==name];assert all(r.unsafe_violation==0 for r in q)
 # Explicit is expected to expose a receipt-authenticity weakness under the conflict profile, not be silently patched.
 q=[r for r in rows if r.condition=='explicit_minimal' and r.workflow.endswith('::receipt_conflict')]; assert any(r.unsafe_violation==1 for r in q)
