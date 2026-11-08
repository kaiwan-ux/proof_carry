from pathlib import Path
from crossresumebench_v3_reva.models import NativePause
from crossresumebench_v3_reva.ledger import FileLedger
from crossresumebench_v3_reva.runner import run
from crossresumebench_v3_reva.analysis import analyze

class Fake:
    def __init__(self,name): self.name=name
    def self_resume_committed(self,run_dir): return {"safe":True,"ledger":{"effect_count":1,"ack_count":1,"finish_count":1}}
    def capture_effect_pause(self,run_dir,world):
        c=1 if world=="committed" else 0
        return NativePause(self.name,"effect_commit_two_worlds",f"{self.name}-cp","fake",["ack"],{"phase":"effect_attempted"},{"framework":self.name},{"effect_count":c,"ack_count":0,"finish_count":0},world)
    def run_from_effect_decision(self,status,run_dir):
        l=FileLedger(Path(run_dir)/"ledger.json"); trace=[]
        if status=="not_committed": l.commit_effect(); trace.append("execute_effect")
        else: trace.append("skip_effect")
        l.ack(); l.finish(); return {"ledger":l.read(),"effect_decision":trace[0],"trace":trace}

def test_full_orchestration_shape(tmp_path):
    rf=lambda n:Fake(n)
    selfr,sr,rows=run(tmp_path,rf)
    assert len(selfr)==3 and len(sr)==6 and len(rows)==72
    v=analyze(tmp_path); assert v["go_for_full_v3"] is True
    assert v["mcc"]=={"rows":24,"safe_completion":12,"safe_rejection":12,"unsafe":0,"technical":0}
