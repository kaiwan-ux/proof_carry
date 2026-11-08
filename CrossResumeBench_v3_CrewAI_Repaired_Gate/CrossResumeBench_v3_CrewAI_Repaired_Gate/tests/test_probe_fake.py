
from pathlib import Path
from crossresumebench_crewai_gate.models import NativePause
from crossresumebench_crewai_gate.ledger import FileLedger
from crossresumebench_crewai_gate.probe import run_probe,SAFE_LEDGER

class FakeRuntime:
    def capability_probe(self): return {"ready":True}
    def self_resume_committed(self,d): return {"restore_completed":True,"safe":True}
    def capture_effect_pause(self,d,world):
        n=1 if world=="committed" else 0
        return NativePause("crewai","effect_commit_two_worlds","cp","fake",["ack"],{}, {}, {"effect_count":n,"ack_count":0,"finish_count":0},world)
    def run_from_effect_decision(self,status,d):
        p=Path(d)/"ledger.json"
        if status=="not_committed": FileLedger(p).commit_effect(); decision="execute_effect"
        else: decision="skip_effect"
        FileLedger(p).ack(); FileLedger(p).finish()
        return {"effect_decision":decision,"ledger":FileLedger(p).read()}

def test_probe_passes_with_good_runtime(tmp_path):
    r=run_probe(tmp_path, runtime_factory=lambda name: FakeRuntime())
    assert r["probe_pass"] is True
    assert len(r["checks"])==6
    assert all(r["checks"].values())
