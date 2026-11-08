from pathlib import Path
from crossresumebench_proofcarry.models import NativePause
from crossresumebench_proofcarry.native_full_study import run_native_full, DEFAULT_VARIANTS
from crossresumebench_proofcarry.semantics import apply_source_pause, apply_plan, oracle_plan, expected_final
from crossresumebench_proofcarry.store import SemanticStore

class FakeRuntime:
    def __init__(self,name): self.name=name
    def capability_probe(self):
        return {'framework':self.name,'installed':True,'ready':True,'version':'fake','pause_kind':'fake','semantic_namespace':self.name}
    def capture_case_pause(self,case,run_dir):
        run_dir=Path(run_dir); store=run_dir/'semantic_store.json'; apply_source_pause(case,store)
        return NativePause(self.name,case.case_id,f'fake:{self.name}:{case.case_id}','fake_checkpoint',['resume'],{'phase':'mid_execution'},{'framework':self.name},SemanticStore(store).read())
    def self_resume_case(self,case,run_dir):
        p=self.capture_case_pause(case,run_dir); store=Path(run_dir)/'semantic_store.json'; apply_plan(oracle_plan(case),store)
        d=SemanticStore(store).read(); a=dict(d); b=dict(expected_final(case)); a.pop('trace',None); b.pop('trace',None)
        return {'restore_completed':True,'safe':a==b,'store':d,'pause':p.to_dict(),'lifecycle_returned':True}
    def run_plan(self,case,plan,run_dir):
        store=Path(run_dir)/'semantic_store.json'; apply_plan(plan,store)
        return {'store':SemanticStore(store).read(),'native_kind':'fake_target'}

def factory(name): return FakeRuntime(name)

def test_native_full_smoke_shape_and_no_technical(tmp_path):
    meta=run_native_full(tmp_path,case_preset='smoke8',profile='proofcarry',variants=DEFAULT_VARIANTS,runtime_factory=factory)
    assert meta['actual']['family_gate_rows']==24
    assert meta['actual']['self_resume_rows']==24
    assert meta['actual']['source_capture_rows']==24
    assert meta['actual']['migration_rows']==8*6*5
    import csv
    with (tmp_path/'native_runs.csv').open(newline='',encoding='utf-8') as f: rows=list(csv.DictReader(f))
    assert len(rows)==240
    assert all(int(r['technical_failure'])==0 for r in rows)
    assert all(int(r['unsafe_violation'])==0 for r in rows if r['method']=='proofcarry')
