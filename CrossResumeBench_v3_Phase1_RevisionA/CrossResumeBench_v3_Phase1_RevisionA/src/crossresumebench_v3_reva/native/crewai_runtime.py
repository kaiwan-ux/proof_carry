from __future__ import annotations
from pathlib import Path
from ..models import NativePause
from ..ledger import FileLedger

class Phase1ControlledPause(RuntimeError): pass

class CrewAIRuntime:
    name="crewai"
    def capability_probe(self):
        import crewai
        from crewai.flow.flow import Flow
        from crewai import CheckpointConfig
        return {"framework":self.name,"installed":True,"version":getattr(crewai,"__version__","unknown"),"flow_from_checkpoint":hasattr(Flow,"from_checkpoint"),"checkpoint_config":CheckpointConfig is not None,"pause_kind":"checkpoint_after_method_then_controlled_stop"}
    def _flow_class(self,checkpoint_cfg=None):
        from crewai.flow.flow import Flow,start,listen
        from pydantic import BaseModel
        class St(BaseModel):
            ledger_path:str=""
            world:str="committed"
            gate_path:str=""
            phase:str="start"
        class F(Flow[St]):
            suppress_flow_events=True
            @start()
            def effect_attempt(self):
                if self.state.world=="committed": FileLedger(Path(self.state.ledger_path)).commit_effect()
                self.state.phase="effect_attempted"; return "attempted"
            @listen(effect_attempt)
            def ack(self,_=None):
                if not Path(self.state.gate_path).exists(): raise Phase1ControlledPause("PHASE1_CHECKPOINT_STOP")
                FileLedger(Path(self.state.ledger_path)).ack(); self.state.phase="acked"; return "acked"
            @listen(ack)
            def finish(self,_=None): FileLedger(Path(self.state.ledger_path)).finish(); self.state.phase="finished"; return "finished"
        return F
    def _checkpoints(self,cpdir): return sorted(Path(cpdir).glob("*.json"),key=lambda p:(p.stat().st_mtime_ns,p.name))
    def capture_effect_pause(self,run_dir,world):
        from crewai import CheckpointConfig
        from crewai.state import JsonProvider
        run_dir=Path(run_dir); cpdir=run_dir/"checkpoints"; cpdir.mkdir(parents=True,exist_ok=True); ledger=run_dir/"ledger.json"; gate=run_dir/"resume.gate"
        cfg=CheckpointConfig(location=str(cpdir),on_events=["method_execution_finished"],provider=JsonProvider(),max_checkpoints=10)
        F=self._flow_class(); f=F(checkpoint=cfg); f.state.ledger_path=str(ledger); f.state.world=world; f.state.gate_path=str(gate)
        paused=False
        try: f.kickoff()
        except Exception as e:
            # CrewAI may wrap listener exceptions. The external ledger/checkpoint assertions below are authoritative.
            paused=True
        cps=self._checkpoints(cpdir); d=FileLedger(ledger).read(); expected=1 if world=="committed" else 0
        if not cps: raise RuntimeError("CrewAI produced no method_execution_finished checkpoint before controlled stop")
        if d!={"effect_count":expected,"ack_count":0,"finish_count":0}: raise RuntimeError(f"CrewAI did not stop before ack: {d}")
        chosen=cps[0]
        return NativePause(self.name,"effect_commit_two_worlds",str(chosen),"crewai_flow_checkpoint",["ack"],{"phase":"effect_attempted"},{"framework":self.name,"checkpoint_file":str(chosen),"checkpoint_count":len(cps),"flow_id":str(f.state.id),"controlled_stop_observed":paused},d,world)
    def self_resume_committed(self,run_dir):
        from crewai import CheckpointConfig
        p=self.capture_effect_pause(run_dir,"committed"); gate=Path(run_dir)/"resume.gate"; gate.write_text("resume",encoding="utf-8")
        F=self._flow_class(); restored=F.from_checkpoint(CheckpointConfig(restore_from=p.checkpoint_ref)); restored.suppress_flow_events=True; restored.kickoff()
        d=FileLedger(Path(run_dir)/"ledger.json").read(); return {"safe":d=={"effect_count":1,"ack_count":1,"finish_count":1},"ledger":d,"pause":p.to_dict()}
    def run_from_effect_decision(self,effect_status,run_dir):
        from crewai.flow.flow import Flow,start,listen
        from pydantic import BaseModel
        ledger=Path(run_dir)/"ledger.json"; trace=[]
        class St(BaseModel): ledger_path:str=""; effect_status:str=""; phase:str="resume"
        class T(Flow[St]):
            suppress_flow_events=True
            @start()
            def effect_guard(self):
                if self.state.effect_status=="not_committed": FileLedger(Path(self.state.ledger_path)).commit_effect(); trace.append("execute_effect")
                elif self.state.effect_status=="committed": trace.append("skip_effect")
                else: raise RuntimeError(f"missing effect decision: {self.state.effect_status!r}")
                self.state.phase="effect_resolved"; return "resolved"
            @listen(effect_guard)
            def ack(self,_=None): FileLedger(Path(self.state.ledger_path)).ack(); trace.append("ack"); self.state.phase="acked"; return "acked"
            @listen(ack)
            def finish(self,_=None): FileLedger(Path(self.state.ledger_path)).finish(); trace.append("finish"); self.state.phase="finished"; return "finished"
        t=T(); t.state.ledger_path=str(ledger); t.state.effect_status=effect_status; out=t.kickoff()
        return {"ledger":FileLedger(ledger).read(),"effect_decision":trace[0] if trace else "","trace":trace,"native_kind":"crewai_target_flow","flow_id":str(t.state.id),"result":str(out)}
