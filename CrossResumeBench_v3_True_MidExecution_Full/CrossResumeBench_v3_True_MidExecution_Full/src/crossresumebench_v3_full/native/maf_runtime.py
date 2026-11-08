from __future__ import annotations
import asyncio,json
from pathlib import Path
from ..models import NativePause
from ..store import SemanticStore
from ..semantics import apply_source_pause,apply_plan,oracle_plan,expected_final

class MAFRuntime:
    name="maf"
    def capability_probe(self):
        import agent_framework
        from agent_framework import FileCheckpointStorage,WorkflowBuilder,handler
        return {"framework":self.name,"installed":True,"version":getattr(agent_framework,"__version__","unknown"),"ready":bool(FileCheckpointStorage and WorkflowBuilder and handler),"pause_kind":"superstep_completed_file_checkpoint","explicit_handler_types":True}
    @staticmethod
    def _enc(d): return json.dumps(d,sort_keys=True,separators=(",",":"))
    @staticmethod
    def _dec(s): return json.loads(s)
    def _source(self,case,storage,name):
        from agent_framework import Executor,WorkflowBuilder,handler
        outer=self
        class Boundary(Executor):
            def __init__(self,*a,**kw): super().__init__(*a,**kw); self.called=False
            @handler(input=str,output=str)
            async def process(self,message,ctx):
                self.called=True; d=outer._dec(message); apply_source_pause(case,d["store_path"]); d["phase"]="paused"; await ctx.send_message(outer._enc(d))
        class Resume(Executor):
            @handler(input=str,workflow_output=str)
            async def process(self,message,ctx):
                d=outer._dec(message); apply_plan(oracle_plan(case),d["store_path"]); d["phase"]="finished"; await ctx.yield_output(outer._enc(d))
        bnd=Boundary(id="source_boundary"); res=Resume(id="resume"); b=WorkflowBuilder(name=name,start_executor=bnd,checkpoint_storage=storage); b.add_edge(bnd,res); return b.build(),bnd
    async def _capture(self,case,run_dir):
        from agent_framework import FileCheckpointStorage
        run_dir=Path(run_dir); cpdir=run_dir/"checkpoints"; storage=FileCheckpointStorage(str(cpdir)); name=f"full-{case.case_id}-{run_dir.name}"; wf,bnd=self._source(case,storage,name); initial=self._enc({"store_path":str(run_dir/"semantic_store.json"),"case_id":case.case_id,"phase":"start"}); events=[]; stopped=False
        async for ev in wf.run(initial,stream=True):
            et=getattr(ev,"type",None); cn=ev.__class__.__name__; events.append({"type":str(et),"class":cn})
            if bnd.called and (et=="superstep_completed" or cn=="SuperStepCompletedEvent"): stopped=True; break
        if not stopped: raise RuntimeError(f"MAF no superstep_completed after source boundary: {events}")
        latest=await storage.get_latest(workflow_name=wf.name)
        if latest is None: raise RuntimeError("MAF checkpoint storage empty")
        cps=await storage.list_checkpoints(workflow_name=wf.name)
        p=NativePause(self.name,case.case_id,str(latest.checkpoint_id),"maf_superstep_file_checkpoint",["resume"],{"phase":"mid_execution"},{"framework":self.name,"workflow_name":wf.name,"checkpoint_id":str(latest.checkpoint_id),"checkpoint_count":len(cps),"event_trace":events,"handler_typing_mode":"explicit"},SemanticStore(run_dir/"semantic_store.json").read())
        return p,cpdir,wf.name,latest.checkpoint_id
    def capture_case_pause(self,case,run_dir): return asyncio.run(self._capture(case,run_dir))[0]
    async def _self(self,case,run_dir):
        from agent_framework import FileCheckpointStorage
        p,cpdir,name,cid=await self._capture(case,run_dir); storage=FileCheckpointStorage(str(cpdir)); wf,_=self._source(case,storage,name)
        async for _ in wf.run(checkpoint_id=cid,checkpoint_storage=storage,stream=True): pass
        d=SemanticStore(Path(run_dir)/"semantic_store.json").read(); return {"restore_completed":True,"safe":_eq(expected_final(case),d),"store":d,"pause":p.to_dict()}
    def self_resume_case(self,case,run_dir): return asyncio.run(self._self(case,run_dir))
    async def _target(self,case,plan,run_dir):
        from agent_framework import Executor,WorkflowBuilder,handler
        outer=self; trace=[]
        class Plan(Executor):
            @handler(input=str,workflow_output=str)
            async def process(self,message,ctx):
                d=outer._dec(message); apply_plan(plan,d["store_path"]); trace.extend(plan); await ctx.yield_output(outer._enc({"done":True}))
        ex=Plan(id="resume_plan"); wf=WorkflowBuilder(name=f"target-{case.case_id}-{Path(run_dir).name}",start_executor=ex).build(); initial=self._enc({"store_path":str(Path(run_dir)/"semantic_store.json")})
        async for _ in wf.run(initial,stream=True): pass
        return {"store":SemanticStore(Path(run_dir)/"semantic_store.json").read(),"trace":trace,"native_kind":"maf_target_workflow_explicit_handlers"}
    def run_plan(self,case,plan,run_dir): return asyncio.run(self._target(case,plan,run_dir))
def _eq(a,b):
    a=dict(a); b=dict(b); a.pop("trace",None); b.pop("trace",None); return a==b
