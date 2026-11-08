from types import SimpleNamespace
from portaflow_pcc.models import LogicalState, SourceCapture
from portaflow_pcc.scenarios import source_prefix_transition, continuation_transition
from portaflow_pcc.orchestrator import run

class FakeAdapter:
    def __init__(self,name): self.name=name
    def run_source(self,wf):
        s=LogicalState(workflow=wf,request_id=f'pcc-{wf}-001'); ld={}; out=source_prefix_transition(s,ld)
        return SourceCapture(self.name,wf,out.to_dict(),{'kind':f'{self.name}_native'},ld)
    def run_target(self,wf,imported,ledger):
        return continuation_transition(imported,ledger),{'kind':f'{self.name}_target_native'}

def test_full_matrix_shape_and_expected_scr(tmp_path):
    cfg={
        'experiment_name':'test','frameworks':['langgraph','crewai','maf'],
        'workflows':['retry','approval','side_effect','branch','loop','parallel'],
        'conditions':['state_only','state_history','plus_control_frontier','plus_pending_obligations','plus_effect_receipts','full_pcc_v0']
    }
    rows=run(cfg,tmp_path,adapter_getter=lambda n:FakeAdapter(n))
    assert len(rows)==216
    assert len({r.run_id for r in rows})==216
    assert sum(r.technical_failure for r in rows)==0
    by={c:[r for r in rows if r.condition==c] for c in cfg['conditions']}
    expected={'state_only':0,'state_history':6,'plus_control_frontier':18,'plus_pending_obligations':24,'plus_effect_receipts':30,'full_pcc_v0':36}
    for c,n in expected.items():
        assert sum(r.safe_continuation for r in by[c])==n,(c,sum(r.safe_continuation for r in by[c]))
