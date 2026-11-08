from pathlib import Path
from crossresumebench_mccv3.models import NativePause
from crossresumebench_mccv3.semantics import apply_source_pause,apply_plan,oracle_plan,expected_final
from crossresumebench_mccv3.store import SemanticStore
class Fake:
    def __init__(self,name): self.name=name
    def capture_case_pause(self,c,rd):
        rd=Path(rd); p=rd/'semantic_store.json'; apply_source_pause(c,p); return NativePause(self.name,c.case_id,'fake:'+c.case_id,'fake_checkpoint',['resume'],{'phase':'mid_execution'},{'framework':self.name},SemanticStore(p).read())
    def self_resume_case(self,c,rd):
        n=self.capture_case_pause(c,rd); apply_plan(oracle_plan(c),Path(rd)/'semantic_store.json'); d=SemanticStore(Path(rd)/'semantic_store.json').read(); e=expected_final(c); d.pop('trace',None);e.pop('trace',None);return {'restore_completed':True,'safe':d==e}
    def run_plan(self,c,plan,rd): apply_plan(plan,Path(rd)/'semantic_store.json'); return {'store':SemanticStore(Path(rd)/'semantic_store.json').read(),'native_kind':'fake'}
def factory(name): return Fake(name)
