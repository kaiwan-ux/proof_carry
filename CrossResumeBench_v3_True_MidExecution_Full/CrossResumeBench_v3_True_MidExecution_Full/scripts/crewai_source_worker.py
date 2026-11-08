from __future__ import annotations
import json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path[:0]=[str(ROOT/"src"),str(ROOT/"frozen_v2"/"src")]
from crossresumebench_v3_full.cases import CASE_BY_ID
from crossresumebench_v3_full.semantics import apply_source_pause,apply_plan,oracle_plan

class SourceStop(RuntimeError): pass

def main(cfg_path):
    from crewai import CheckpointConfig
    from crewai.flow.flow import Flow,listen,start
    from crewai.state import JsonProvider
    from pydantic import BaseModel
    cfg=json.loads(Path(cfg_path).read_text(encoding="utf-8")); case=CASE_BY_ID[cfg["case_id"]]
    class St(BaseModel):
        store_path:str=""; case_id:str=""; resume_gate:str=""; stop_gate:str=""; signal:str=""; phase:str="start"
    class F(Flow[St]):
        @start()
        def source_boundary(self):
            apply_source_pause(case,self.state.store_path); self.state.phase="paused"; Path(self.state.signal).write_text("ready",encoding="utf-8"); return "paused"
        @listen(source_boundary)
        def resume(self,_=None):
            while True:
                if Path(self.state.resume_gate).exists(): apply_plan(oracle_plan(case),self.state.store_path); self.state.phase="finished"; return "finished"
                if Path(self.state.stop_gate).exists(): raise SourceStop("FULL_V3_CHECKPOINT_CAPTURED")
                time.sleep(0.05)
    cp=CheckpointConfig(location=cfg["checkpoint_dir"],on_events=["method_execution_finished"],provider=JsonProvider(),max_checkpoints=30)
    f=F(checkpoint=cp); f.state.store_path=cfg["store_path"]; f.state.case_id=case.case_id; f.state.resume_gate=cfg["resume_gate"]; f.state.stop_gate=cfg["stop_gate"]; f.state.signal=cfg["signal"]
    try: f.kickoff()
    except SourceStop: return
if __name__=="__main__": main(sys.argv[1])
