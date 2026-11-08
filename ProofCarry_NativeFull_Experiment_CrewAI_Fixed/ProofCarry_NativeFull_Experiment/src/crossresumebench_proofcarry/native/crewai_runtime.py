from __future__ import annotations
import json,os,subprocess,sys,time,shutil
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
        import inspect
        kickoff_params = set(inspect.signature(Flow.kickoff).parameters)
        has_resume = hasattr(Flow,"from_checkpoint") or "from_checkpoint" in kickoff_params
        return {"framework":self.name,"semantic_namespace":"crew.task","pause_status":"pending","identifier_label":"task_id","installed":True,"version":getattr(crewai,"__version__","unknown"),"ready":bool(has_resume and CheckpointConfig and JsonProvider),"pause_kind":"flow_checkpoint_external_gate","supports_class_from_checkpoint":bool(hasattr(Flow,"from_checkpoint")),"supports_kickoff_from_checkpoint":bool("from_checkpoint" in kickoff_params)}
    @staticmethod
    def _checkpoints(cpdir): return sorted([p for p in Path(cpdir).rglob("*") if p.is_file() and p.suffix.lower() in {".json",".checkpoint"}],key=lambda p:(p.stat().st_mtime_ns,str(p)))
    @staticmethod
    def _quiet_env(env):
        # Force, rather than setdefault: a parent shell may already export a
        # tracing preference.  Native benchmark workers must be deterministic
        # and non-interactive regardless of the user's local CrewAI settings.
        env.update({
            "CREWAI_TRACING_ENABLED":"false",
            "CREWAI_DISABLE_TELEMETRY":"true",
            "CREWAI_DISABLE_TRACKING":"true",
            "CREWAI_TELEMETRY_OPT_OUT":"true",
            "OTEL_SDK_DISABLED":"true",
            "PYTHONUTF8":"1",
            "PYTHONIOENCODING":"utf-8",
            "PYTHONUNBUFFERED":"1",
        })
        return env
    @staticmethod
    def _quiet_resume_flow(flow):
        from crewai.events.listeners.tracing.utils import set_tracing_enabled
        # CrewAI 1.15.17 treats only env=true as authoritative and may fall
        # back to saved user consent for env=false. Force the ContextVar off.
        set_tracing_enabled(False)
        # Checkpoint persistence is already complete when this is called.  The
        # resumed benchmark flow does not need observability lifecycle events;
        # disabling them prevents CrewAI trace/finalization handlers from
        # keeping kickoff alive after semantic completion.  This does NOT mask
        # a hang: kickoff itself must still return for the native gate to pass.
        if hasattr(flow,"tracing"): flow.tracing=False
        if hasattr(flow,"defer_trace_finalization"): flow.defer_trace_finalization=False
        if hasattr(flow,"suppress_flow_events"): flow.suppress_flow_events=True
        if hasattr(flow,"stream"): flow.stream=False
        return flow
    def _worker(self,case,run_dir,on_events=None):
        root=Path(__file__).resolve().parents[3]; cfg={"run_dir":str(run_dir),"case_id":case.case_id,"checkpoint_dir":str(run_dir/"checkpoints"),"store_path":str(run_dir/"semantic_store.json"),"resume_gate":str(run_dir/"resume.gate"),"stop_gate":str(run_dir/"stop.gate"),"signal":str(run_dir/"source_ready.signal"),"on_events":list(on_events or ["method_execution_finished"])}; cp=run_dir/"worker_config.json"; cp.write_text(json.dumps(cfg,indent=2),encoding="utf-8")
        env=self._quiet_env(os.environ.copy())
        fo=(run_dir/"worker_stdout.txt").open("wb"); fe=(run_dir/"worker_stderr.txt").open("wb")
        proc=subprocess.Popen([sys.executable,"-u",str(root/"scripts"/"crewai_source_worker.py"),str(cp)],cwd=str(root),env=env,stdout=fo,stderr=fe)
        proc._crb_streams=(fo,fe)
        return proc
    def _checkpoint_mentions_pause(self,p,case_id):
        try:
            txt=Path(p).read_text(encoding="utf-8",errors="replace")
            # Require this case and a paused/source-boundary marker.  Exclude a
            # terminal state if a release emitted an additional late snapshot.
            return (case_id in txt and ("paused" in txt or "source_boundary" in txt) and '"phase": "finished"' not in txt and '"phase":"finished"' not in txt)
        except Exception:
            return False
    def _capture_attempt(self,case,run_dir,on_events,mode):
        # Clean transient control files/checkpoints before each attempt.
        for name in ["resume.gate","stop.gate","source_ready.signal","worker_stdout.txt","worker_stderr.txt"]:
            try:(run_dir/name).unlink()
            except FileNotFoundError:pass
        cpdir=run_dir/"checkpoints"; shutil.rmtree(cpdir,ignore_errors=True); cpdir.mkdir(parents=True,exist_ok=True)
        proc=self._worker(case,run_dir,on_events=on_events); deadline=time.time()+45; cps=[]
        try:
            while time.time()<deadline:
                if proc.poll() is not None:
                    self._close_streams(proc)
                    out=(run_dir/"worker_stdout.txt").read_text(encoding="utf-8",errors="replace") if (run_dir/"worker_stdout.txt").exists() else ""
                    err=(run_dir/"worker_stderr.txt").read_text(encoding="utf-8",errors="replace") if (run_dir/"worker_stderr.txt").exists() else ""
                    raise RuntimeError(f"CrewAI worker exited early rc={proc.returncode}\nOUT={out}\nERR={err}")
                if (run_dir/"source_ready.signal").exists():
                    raw=self._checkpoints(cpdir)
                    paused=[p for p in raw if self._checkpoint_mentions_pause(p,case.case_id)]
                    cps=paused or raw
                    if cps: break
                time.sleep(.05)
            if not cps: raise RuntimeError(f"CrewAI produced no persisted checkpoint in mode={mode}, events={on_events}")
            chosen=cps[-1]; (run_dir/"stop.gate").write_text("stop",encoding="utf-8")
            try: proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.terminate()
                try: proc.wait(timeout=5)
                except subprocess.TimeoutExpired: proc.kill(); proc.wait(timeout=5)
            self._close_streams(proc)
            return NativePause(self.name,case.case_id,str(chosen),"crewai_flow_checkpoint",["resume"],{"phase":"mid_execution"},{"framework":self.name,"semantic_namespace":"crew.task","pause_status":"pending","identifier_label":"task_id","checkpoint_file":str(chosen),"checkpoint_count":len(cps),"pause_protocol":"subprocess_external_gate","checkpoint_event_mode":mode},SemanticStore(run_dir/"semantic_store.json").read())
        finally:
            if proc.poll() is None:
                proc.terminate()
                try: proc.wait(timeout=3)
                except Exception:
                    try: proc.kill()
                    except Exception: pass
            self._close_streams(proc)
    def capture_case_pause(self,case,run_dir):
        run_dir=Path(run_dir); run_dir.mkdir(parents=True,exist_ok=True); (run_dir/"checkpoints").mkdir(exist_ok=True)
        errors=[]
        # Strict event first. If a CrewAI release does not persist that event,
        # retry with all events, while still requiring a real persisted checkpoint.
        for events,mode in [(["method_execution_finished"],"method_execution_finished"),(["*"],"all_events_fallback")]:
            try:return self._capture_attempt(case,run_dir,events,mode)
            except Exception as e:errors.append(f"{mode}: {e}")
        raise RuntimeError("CrewAI checkpoint capture failed under both supported event profiles: " + " | ".join(errors))
    @staticmethod
    def _close_streams(proc):
        for h in getattr(proc,"_crb_streams",()):
            try:
                if not h.closed: h.close()
            except Exception: pass
    @staticmethod
    def _restore_class(case):
        from crewai.flow.flow import Flow,listen,start
        from pydantic import BaseModel
        class St(BaseModel): store_path:str=""; case_id:str=""; resume_gate:str=""; stop_gate:str=""; signal:str=""; phase:str="paused"
        class F(Flow[St]):
            tracing: bool | None = False
            @start()
            def source_boundary(self):
                # This should NOT run when resuming - phase should already be "paused"
                from ..semantics import apply_source_pause
                apply_source_pause(case,self.state.store_path)
                self.state.phase="paused"
                return "paused"
            @listen(source_boundary)
            def resume(self,_=None):
                # When resuming from checkpoint, start here directly
                apply_plan(oracle_plan(case),self.state.store_path)
                self.state.phase="finished"
                return "finished"
        return F
    def self_resume_case(self,case,run_dir):
        from crewai import CheckpointConfig
        import inspect
        # The isolated operation worker imports CrewAI before entering this
        # adapter, so configure the current process as well as child workers.
        # Otherwise trace finalization can outlive correct semantic completion.
        self._quiet_env(os.environ)
        run_dir=Path(run_dir); p=self.capture_case_pause(case,run_dir); F=self._restore_class(case)
        cfg=CheckpointConfig(restore_from=p.checkpoint_ref)
        errors=[]; mode=None
        # Compatibility across CrewAI checkpoint releases: prefer the class
        # constructor when present, otherwise pass CheckpointConfig to kickoff.
        if hasattr(F,"from_checkpoint"):
            try:
                f=self._quiet_resume_flow(F.from_checkpoint(cfg)); f.kickoff(); mode="Flow.from_checkpoint"
            except Exception as e: errors.append(f"Flow.from_checkpoint: {e}"); mode=None
        if mode is None:
            try:
                f=self._quiet_resume_flow(F())
                if "from_checkpoint" not in inspect.signature(f.kickoff).parameters:
                    raise RuntimeError("kickoff has no from_checkpoint parameter")
                f.kickoff(from_checkpoint=cfg); mode="kickoff(from_checkpoint=...)"
            except Exception as e: errors.append(f"kickoff(from_checkpoint): {e}"); raise RuntimeError("CrewAI resume failed: " + " | ".join(errors))
        d=SemanticStore(run_dir/"semantic_store.json").read(); return {"restore_completed":True,"safe":_eq(expected_final(case),d),"store":d,"pause":p.to_dict(),"resume_api":mode}
    def run_plan(self,case,plan,run_dir):
        from crewai.flow.flow import Flow,start,listen
        from pydantic import BaseModel
        self._quiet_env(os.environ)
        store=Path(run_dir)/"semantic_store.json"; trace=[]
        class St(BaseModel): store_path:str=""; phase:str="resume"
        class T(Flow[St]):
            tracing: bool | None = False
            @start()
            def execute(self): apply_plan(plan,self.state.store_path); trace.extend(plan); self.state.phase="applied"; return "applied"
            @listen(execute)
            def finish(self,_=None): self.state.phase="finished"; return "finished"
        t=self._quiet_resume_flow(T()); t.state.store_path=str(store); result=t.kickoff(); return {"store":SemanticStore(store).read(),"trace":trace,"native_kind":"crewai_target_flow","result":str(result)}
def _eq(a,b):
    a=dict(a); b=dict(b); a.pop("trace",None); b.pop("trace",None); return a==b
