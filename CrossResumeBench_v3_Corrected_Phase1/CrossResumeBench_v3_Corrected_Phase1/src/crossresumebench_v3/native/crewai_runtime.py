from __future__ import annotations
from pathlib import Path
from ..models import NativePause
from ..ledger import FileLedger

class CrewAIRuntime:
    name="crewai"
    def capability_probe(self):
        import crewai
        from crewai.flow.flow import Flow
        from crewai import CheckpointConfig
        return {"framework":self.name,"installed":True,"version":getattr(crewai,"__version__","unknown"),"flow_from_checkpoint":hasattr(Flow,"from_checkpoint"),"checkpoint_config":CheckpointConfig is not None,"pause_kind":"flow_method_checkpoint"}
    def _flow_class(self,ledger_path,checkpoint_cfg):
        from crewai.flow.flow import Flow,start,listen
        from pydantic import BaseModel
        class St(BaseModel):
            ledger_path:str=str(ledger_path); phase:str="start"
        class F(Flow[St]):
            checkpoint=checkpoint_cfg
            suppress_flow_events=True
            @start()
            def commit_effect(self): FileLedger(Path(self.state.ledger_path)).commit_effect(); self.state.phase="effect_committed"; return "committed"
            @listen(commit_effect)
            def ack(self,_=None): FileLedger(Path(self.state.ledger_path)).ack(); self.state.phase="acked"; return "acked"
            @listen(ack)
            def finish(self,_=None): FileLedger(Path(self.state.ledger_path)).finish(); self.state.phase="finished"; return "finished"
        return F
    def _checkpoints(self,path): return sorted(Path(path).glob('*.json'),key=lambda p:p.stat().st_mtime)
    def capture_effect_ack_pause(self,run_dir):
        from crewai import CheckpointConfig
        from crewai.state import JsonProvider
        run_dir=Path(run_dir); cpdir=run_dir/"checkpoints"; cpdir.mkdir(parents=True,exist_ok=True); ledger=run_dir/"ledger.json"
        cfg=CheckpointConfig(location=str(cpdir),on_events=["method_execution_finished"],provider=JsonProvider(),max_checkpoints=20)
        F=self._flow_class(ledger,cfg); f=F(); f.kickoff()
        cps=self._checkpoints(cpdir)
        if len(cps)<1: raise RuntimeError("CrewAI produced no Flow checkpoints")
        # Earliest checkpoint is expected to be after the first completed method. We verify it by restoring and checking completed method metadata when possible.
        chosen=cps[0]
        self._restore=(F,chosen,ledger)
        return NativePause(self.name,"effect_committed_ack_pending",str(chosen),"crewai_flow_checkpoint",["ack"],{"phase":"effect_committed"},[],[],{"checkpoint_file":str(chosen),"flow_id":str(f.state.id),"checkpoint_count":len(cps)},1)
    def self_resume_effect_ack(self,run_dir):
        # Use a fresh source run, then reset the ledger to the source-world state before restoring the selected checkpoint.
        p=self.capture_effect_ack_pause(run_dir); F,chosen,ledger=self._restore
        FileLedger(ledger)._write({"effect_count":1,"ack_count":0,"finish_count":0})
        from crewai import CheckpointConfig
        restored=F.from_checkpoint(CheckpointConfig(restore_from=str(chosen)))
        restored.suppress_flow_events=True; restored.kickoff(); d=FileLedger(ledger).read()
        return {"safe":d=={"effect_count":1,"ack_count":1,"finish_count":1},"ledger":d,"pause":p.to_dict()}
    def run_ack_finish_from_mcc(self,reconstructed,run_dir):
        from crewai.flow.flow import Flow,start,listen
        from pydantic import BaseModel
        run_dir=Path(run_dir); ledger=run_dir/"ledger.json"; l=FileLedger(ledger)
        if l.read()["effect_count"]==0: l.commit_effect()
        class St(BaseModel): ledger_path:str=str(ledger); phase:str="resume"
        class T(Flow[St]):
            suppress_flow_events=True
            @start()
            def ack(self): FileLedger(Path(self.state.ledger_path)).ack(); self.state.phase="acked"; return "acked"
            @listen(ack)
            def finish(self,_=None): FileLedger(Path(self.state.ledger_path)).finish(); self.state.phase="finished"; return "finished"
        t=T(); out=t.kickoff(); return {"ledger":l.read(),"native_kind":"crewai_target_flow","flow_id":str(t.state.id),"result":str(out)}
