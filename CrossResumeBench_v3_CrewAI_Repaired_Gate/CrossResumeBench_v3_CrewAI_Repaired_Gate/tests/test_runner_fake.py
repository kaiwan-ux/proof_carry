
from pathlib import Path
from crossresumebench_crewai_gate.models import NativePause
from crossresumebench_crewai_gate.ledger import FileLedger
from crossresumebench_crewai_gate.runner import run,SAFE_LEDGER
from crossresumebench_crewai_gate.analysis import analyze

class FakeRuntime:
    name="crewai"
    def capability_probe(self): return {"ready":True,"framework":"crewai","version":"fake"}
    def self_resume_committed(self,run_dir):
        return {"restore_completed":True,"safe":True,"unsafe_native_replay":False,"ledger":SAFE_LEDGER}
    def capture_effect_pause(self,run_dir,world):
        count=1 if world=="committed" else 0
        return NativePause("crewai","effect_commit_two_worlds",f"fake-cp-{world}","fake",["ack"],{"phase":"effect_attempted"},{"framework":"crewai"},{"effect_count":count,"ack_count":0,"finish_count":0},world)
    def run_from_effect_decision(self,effect_status,run_dir):
        ledger=Path(run_dir)/"ledger.json"; trace=[]
        if effect_status=="not_committed": FileLedger(ledger).commit_effect(); trace.append("execute_effect")
        else: trace.append("skip_effect")
        FileLedger(ledger).ack(); FileLedger(ledger).finish()
        return {"ledger":FileLedger(ledger).read(),"effect_decision":trace[0],"trace":trace}

def factory(name):
    assert name=="crewai"
    return FakeRuntime()

def test_fake_full_gate(tmp_path):
    results=tmp_path/"results"
    run(results,runtime_factory=factory)
    verdict=analyze(results)
    assert verdict["crewai_repaired_gate_pass"] is True
    assert verdict["all_migrations"]=={"safe_completion":10,"safe_rejection":2,"unsafe":0,"technical":0}
    assert verdict["mcc"]=={"rows":4,"safe_completion":2,"safe_rejection":2,"unsafe":0,"technical":0}
