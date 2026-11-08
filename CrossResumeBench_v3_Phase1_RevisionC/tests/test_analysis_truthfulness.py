import json
from pathlib import Path
from crossresumebench_v3_revc.models import NativePause
from crossresumebench_v3_revc.ledger import FileLedger
from crossresumebench_v3_revc.runner import run
from crossresumebench_v3_revc.analysis import analyze

class Fake:
    def __init__(self,name): self.name=name
    def self_resume_committed(self,run_dir): return {"restore_completed":True,"safe":True,"ledger":{"effect_count":1,"ack_count":1,"finish_count":1}}
    def capture_effect_pause(self,run_dir,world):
        c=1 if world=="committed" else 0
        return NativePause(self.name,"effect_commit_two_worlds",f"{self.name}-cp","fake",["ack"],{"phase":"effect_attempted"},{"framework":self.name},{"effect_count":c,"ack_count":0,"finish_count":0},world)
    def run_from_effect_decision(self,status,run_dir):
        l=FileLedger(Path(run_dir)/"ledger.json"); trace=[]
        if status=="not_committed": l.commit_effect(); trace.append("execute_effect")
        else: trace.append("skip_effect")
        l.ack(); l.finish(); return {"ledger":l.read(),"effect_decision":trace[0],"trace":trace}

def test_generated_pair_facts_match_rows(tmp_path):
    run(tmp_path,lambda n:Fake(n))
    (tmp_path/"MAF_REVISIONC_PROBE.json").write_text(json.dumps({"pass": True}))
    v=analyze(tmp_path)
    assert len(v["pair_facts"])==6
    assert all(p["rows"]==12 for p in v["pair_facts"])
    assert all(p["safe_completion"]==10 and p["safe_rejection"]==2 and p["unsafe"]==0 and p["technical"]==0 for p in v["pair_facts"])
    assert all(x["certified_worlds_correct"] for x in v["certified_world_disambiguation"])
