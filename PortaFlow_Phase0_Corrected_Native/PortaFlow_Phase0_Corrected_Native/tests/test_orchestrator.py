import json
from pathlib import Path
from portaflow_native.models import SourceCapture, LogicalState
from portaflow_native.scenarios import initial_state, source_prefix_transition, continuation_transition
import portaflow_native.orchestrator as orch

class FakeAdapter:
    def __init__(self,name): self.name=name
    def run_source(self,w):
        led={}; s=source_prefix_transition(initial_state(w),led)
        return SourceCapture(self.name,w,s.to_dict(),{"kind":f"{self.name}_fake_native"},led)
    def run_target(self,w,imported,ledger):
        out=continuation_transition(imported,ledger)
        return out,{"kind":f"{self.name}_fake_target"}

def test_matrix_shape_and_expected_conditions(tmp_path,monkeypatch):
    monkeypatch.setattr(orch,"adapter",lambda name: FakeAdapter(name))
    cfg={"experiment_name":"t","frameworks":["langgraph","crewai","maf"],"workflows":["retry","approval","side_effect"],"conditions":["naive_state","state_history","native_semantic"]}
    rows=orch.run(cfg,tmp_path)
    assert len(rows)==54
    assert len({r.run_id for r in rows})==54
    assert sum(r.technical_failure for r in rows)==0
    by={}
    for r in rows: by.setdefault((r.workflow,r.condition),set()).add(r.safe_continuation)
    assert by[("retry","naive_state")]=={0}
    assert by[("approval","naive_state")]=={0}
    assert by[("side_effect","naive_state")]=={0}
    assert by[("retry","state_history")]=={1}
    assert by[("approval","state_history")]=={1}
    assert by[("side_effect","state_history")]=={0}
    for w in ["retry","approval","side_effect"]: assert by[(w,"native_semantic")]=={1}
