import json
from pathlib import Path
from portaflow_v1.benchmark import initial_state,source_prefix_transition,continuation_transition
from portaflow_v1.models import SourceCapture
from portaflow_v1.orchestrator import run

class Fake:
    def __init__(self,n): self.n=n
    def run_source(self,wf):
        ld={}; s=source_prefix_transition(initial_state(wf),ld); return SourceCapture(self.n,wf,s.to_dict(),{"kind":f"{self.n}_native"},ld)
    def run_target(self,wf,imported,ledger):
        out=continuation_transition(imported,ledger); return out,{"kind":f"{self.n}_target"}

def test_matrix_shape(tmp_path):
    cfg={"experiment_name":"t","frameworks":["a","b","c"],"workflows":["branch_effect_approval","loop_effect"],"conditions":["state_only","history_inference","full_pcc_v1"]}
    rows=run(cfg,tmp_path,lambda n:Fake(n))
    assert len(rows)==3*2*2*3
    assert len({r.run_id for r in rows})==len(rows)
    assert sum(r.technical_failure for r in rows)==0
    assert sum(r.safe_completion for r in rows if r.condition=="full_pcc_v1")==12
