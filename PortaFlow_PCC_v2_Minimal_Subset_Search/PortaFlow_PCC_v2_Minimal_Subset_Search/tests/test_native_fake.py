import json
from pathlib import Path
from portaflow_min.models import SourceCapture,ExecutionState
from portaflow_min.benchmark import initial_state,source_prefix_transition,continuation_transition
from portaflow_min.native import run_native
class Fake:
    def __init__(self,name): self.name=name
    def run_source(self,wf):
        ld={}; s=source_prefix_transition(initial_state(wf),ld); return SourceCapture(self.name,wf,s.to_dict(),{'kind':f'{self.name}_fake'},ld)
    def run_target(self,wf,imported,ledger): return continuation_transition(imported,ledger),{'kind':f'{self.name}_fake_target'}
def test_native_matrix_fake(tmp_path):
    (tmp_path/'results').mkdir(); cfg={'experiment_name':'t','frameworks':['a','b','c'],'workflows':['approval_loop','retry_effect_uncertain']}
    sel=[{'name':'hist','components':['history'],'inference_mode':'hybrid'},{'name':'hr','components':['history','receipts'],'inference_mode':'hybrid'}]
    rows=run_native(cfg,tmp_path,sel,adapter_getter=lambda n:Fake(n)); assert len(rows)==3*2*2*2; assert sum(x.technical_failure for x in rows)==0
