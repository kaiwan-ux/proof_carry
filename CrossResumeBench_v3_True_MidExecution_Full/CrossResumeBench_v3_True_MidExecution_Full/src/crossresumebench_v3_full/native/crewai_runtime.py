from __future__ import annotations
import json,os,subprocess,sys,time
from pathlib import Path
from ..models import NativePause
from ..store import SemanticStore
from ..semantics import expected_final,apply_plan,oracle_plan

class CrewAIRuntime:
    name="crewai"
    def capability_probe(self):
        import crewai
        from crewai import CheckpointConfig
        from crewai.flow.flow import Flow
        from crewai.state import JsonProvider
        return {"framework":self.name,"installed":True,"version":getattr(crewai,"__version__","unknown"),"ready":bool(hasattr(Flow,"from_checkpoint") and CheckpointConfig and JsonProvider),"pause_kind":"method_execution_finished_checkpoint_external_gate"}
    @staticmethod
    def _checkpoints(cpdir): return sorted([p for p in Path(cpdir).rglob("*") if p.is_file() and p.suffix.lower() in {".json",".checkpoint"}],key=lambda p:(p.stat().st_mtime_ns,str(p)))
    def _worker(self,case,run_dir):
        root=Path(__file__).resolve().parents[3]; cfg={"run_dir":str(run_dir),"case_id":case.case_id,"checkpoint_dir":str(run_dir/"checkpoints"),"store_path":str(run_dir/"semantic_store.json"),"resume_gate":str(run_dir/"resume.gate"),"stop_gate":str(run_dir/"stop.gate"),"signal":str(run_dir/"source_ready.signal")}; cp=run_dir/"worker_config.json"; cp.write_text(json.dumps(cfg,indent=2),encoding="utf-8")
        env=os.environ.copy(); env.setdefault("CREWAI_TRACING_ENABLED","false"); env.setdefault("CREWAI_DISABLE_TELEMETRY","true"); env.setdefault("CREWAI_DISABLE_TRACKING","true"); env.setdefault("OTEL_SDK_DISABLED","true")
        return subprocess.Popen([sys.executable,str(root/"scripts"/"crewai_source_worker.py"),str(cp)],cwd=str(root),env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    def capture_case_pause(self,case,run_dir):
        run_dir=Path(run_dir); run_dir.mkdir(parents=True,exist_ok=True); (run_dir/"checkpoints").mkdir(exist_ok=True); proc=self._worker(case,run_dir); deadline=time.time()+40; cps=[]
        try:
            while time.time()<deadline:
                if proc.poll() is not None:
                    out,err=proc.communicate(timeout=2); raise RuntimeError(f"CrewAI worker exited early rc={proc.returncode}\nOUT={out}\nERR={err}")
                if (run_dir/"source_ready.signal").exists():
                    cps=self._checkpoints(run_dir/"checkpoints")
                    if cps: break
                time.sleep(.05)
            if not cps: raise RuntimeError("CrewAI produced no persisted method_execution_finished checkpoint")
            chosen=cps[-1]; (run_dir/"stop.gate").write_text("stop",encoding="utf-8")
            try: out,err=proc.communicate(timeout=5)
            except subprocess.TimeoutExpired: proc.terminate(); out,err=proc.communicate(timeout=5)
            (run_dir/"worker_stdout.txt").write_text(out or "",encoding="utf-8"); (run_dir/"worker_stderr.txt").write_text(err or "",encoding="utf-8")
            return NativePause(self.name,case.case_id,str(chosen),"crewai_flow_checkpoint",["resume"],{"phase":"mid_execution"},{"framework":self.name,"checkpoint_file":str(chosen),"checkpoint_count":len(cps),"pause_protocol":"subprocess_external_gate"},SemanticStore(run_dir/"semantic_store.json").read())
        finally:
            if proc.poll() is None: proc.terminate()
    @staticmethod
    def _restore_class(case):
        from crewai.flow.flow import Flow,listen,start
        from pydantic import BaseModel
        class St(BaseModel): store_path:str=""; case_id:str=""; resume_gate:str=""; stop_gate:str=""; signal:str=""; phase:str="start"
        class F(Flow[St]):
            @start()
            def source_boundary(self):
                from ..semantics import apply_source_pause
                apply_source_pause(case,self.state.store_path); self.state.phase="paused"; return "paused"
            @listen(source_boundary)
            def resume(self,_=None):
                apply_plan(oracle_plan(case),self.state.store_path); self.state.phase="finished"; return "finished"
        return F
    def self_resume_case(self,case,run_dir):
        from crewai import CheckpointConfig
        run_dir=Path(run_dir); p=self.capture_case_pause(case,run_dir); F=self._restore_class(case); f=F.from_checkpoint(CheckpointConfig(restore_from=p.checkpoint_ref)); f.kickoff(); d=SemanticStore(run_dir/"semantic_store.json").read(); return {"restore_completed":True,"safe":_eq(expected_final(case),d),"store":d,"pause":p.to_dict()}
    def run_plan(self,case,plan,run_dir):
        from crewai.flow.flow import Flow,start,listen
        from pydantic import BaseModel
        store=Path(run_dir)/"semantic_store.json"; trace=[]
        class St(BaseModel): store_path:str=""; phase:str="resume"
        class T(Flow[St]):
            @start()
            def execute(self): apply_plan(plan,self.state.store_path); trace.extend(plan); self.state.phase="applied"; return "applied"
            @listen(execute)
            def finish(self,_=None): self.state.phase="finished"; return "finished"
        t=T(); t.state.store_path=str(store); result=t.kickoff(); return {"store":SemanticStore(store).read(),"trace":trace,"native_kind":"crewai_target_flow","result":str(result)}
def _eq(a,b):
    a=dict(a); b=dict(b); a.pop("trace",None); b.pop("trace",None); return a==b
