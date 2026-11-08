from pathlib import Path
from crossresumebench_v3_full.models import NativePause
from crossresumebench_v3_full.semantics import apply_source_pause,apply_plan,oracle_plan,expected_final
from crossresumebench_v3_full.store import SemanticStore
class FakeRuntime:
    def __init__(self,name): self.name=name
    def capability_probe(self): return {"framework":self.name,"ready":True}
    def capture_case_pause(self,case,run_dir):
        p=Path(run_dir)/"semantic_store.json"; d=apply_source_pause(case,p); return NativePause(self.name,case.case_id,f"fake:{self.name}:{case.case_id}",f"{self.name}_fake_checkpoint",["resume"],{"phase":"mid_execution"},{"framework":self.name},d)
    def self_resume_case(self,case,run_dir):
        p=Path(run_dir)/"semantic_store.json"; apply_source_pause(case,p); apply_plan(oracle_plan(case),p); d=SemanticStore(p).read(); e=expected_final(case); e.pop("trace",None); x=dict(d); x.pop("trace",None); return {"restore_completed":True,"safe":e==x,"store":d}
    def run_plan(self,case,plan,run_dir): apply_plan(plan,Path(run_dir)/"semantic_store.json"); return {"store":SemanticStore(Path(run_dir)/"semantic_store.json").read(),"trace":plan,"native_kind":"fake"}
def factory(name): return FakeRuntime(name)
