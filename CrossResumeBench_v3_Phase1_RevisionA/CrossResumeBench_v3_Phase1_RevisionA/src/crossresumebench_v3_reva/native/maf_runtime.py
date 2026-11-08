from __future__ import annotations
import asyncio
from pathlib import Path
from typing_extensions import Never
from ..models import NativePause
from ..ledger import FileLedger

class MAFRuntime:
    name="maf"
    def capability_probe(self):
        import agent_framework
        from agent_framework import WorkflowBuilder,InMemoryCheckpointStorage
        return {"framework":self.name,"installed":True,"version":getattr(agent_framework,"__version__","unknown"),"workflow_builder":WorkflowBuilder is not None,"checkpoint_storage":InMemoryCheckpointStorage is not None,"pause_kind":"superstep_completed_checkpoint"}
    def _build_source(self,storage,workflow_name):
        from agent_framework import Executor,WorkflowBuilder,WorkflowContext,handler
        class Attempt(Executor):
            def __init__(self,*a,**kw): super().__init__(*a,**kw); self.called=False
            @handler
            async def process(self,message:dict,ctx:WorkflowContext[dict])->None:
                self.called=True
                if message["world"]=="committed": FileLedger(Path(message["ledger_path"])).commit_effect()
                await ctx.send_message({**message,"phase":"effect_attempted"})
        class Ack(Executor):
            @handler
            async def process(self,message:dict,ctx:WorkflowContext[dict])->None:
                FileLedger(Path(message["ledger_path"])).ack(); await ctx.send_message({**message,"phase":"acked"})
        class End(Executor):
            @handler
            async def process(self,message:dict,ctx:WorkflowContext[Never,dict])->None:
                FileLedger(Path(message["ledger_path"])).finish(); await ctx.yield_output({**message,"phase":"finished"})
        a=Attempt(id="effect_attempt"); b=Ack(id="ack"); z=End(id="finish")
        wb=WorkflowBuilder(name=workflow_name,start_executor=a,checkpoint_storage=storage); wb.add_edge(a,b); wb.add_edge(b,z)
        return wb.build(),a
    async def _capture_with_context(self,run_dir,world):
        from agent_framework import InMemoryCheckpointStorage
        run_dir=Path(run_dir); ledger=run_dir/"ledger.json"; storage=InMemoryCheckpointStorage(); wname=f"reva-maf-{run_dir.name}"; wf,attempt=self._build_source(storage,wname)
        stopped=False
        async for event in wf.run(message={"ledger_path":str(ledger),"world":world,"phase":"start"},stream=True):
            if getattr(event,"type",None)=="superstep_completed" and attempt.called:
                stopped=True; break
        if not stopped: raise RuntimeError("MAF did not expose superstep_completed after effect attempt")
        latest=await storage.get_latest(workflow_name=wf.name)
        if latest is None: raise RuntimeError("MAF checkpoint missing after effect-attempt superstep")
        d=FileLedger(ledger).read(); expected=1 if world=="committed" else 0
        if d!={"effect_count":expected,"ack_count":0,"finish_count":0}: raise RuntimeError(f"MAF did not stop before ack: {d}")
        p=NativePause(self.name,"effect_commit_two_worlds",str(latest.checkpoint_id),"maf_superstep_checkpoint",["ack"],{"phase":"effect_attempted"},{"framework":self.name,"workflow_name":wf.name,"checkpoint_id":str(latest.checkpoint_id),"iteration_count":getattr(latest,"iteration_count",None)},d,world)
        return p,storage,wf,latest,ledger
    def capture_effect_pause(self,run_dir,world):
        p,*_=asyncio.run(self._capture_with_context(run_dir,world)); return p
    async def _self_resume_async(self,run_dir):
        p,storage,wf,latest,ledger=await self._capture_with_context(run_dir,"committed")
        async for _ in wf.run(checkpoint_id=latest.checkpoint_id,checkpoint_storage=storage,stream=True): pass
        d=FileLedger(ledger).read(); return {"safe":d=={"effect_count":1,"ack_count":1,"finish_count":1},"ledger":d,"pause":p.to_dict()}
    def self_resume_committed(self,run_dir): return asyncio.run(self._self_resume_async(run_dir))
    async def _target_async(self,effect_status,run_dir):
        from agent_framework import Executor,WorkflowBuilder,WorkflowContext,handler
        ledger=Path(run_dir)/"ledger.json"; trace=[]
        class Guard(Executor):
            @handler
            async def process(self,message:dict,ctx:WorkflowContext[dict])->None:
                status=message["effect_status"]
                if status=="not_committed": FileLedger(Path(message["ledger_path"])).commit_effect(); trace.append("execute_effect")
                elif status=="committed": trace.append("skip_effect")
                else: raise RuntimeError(f"missing effect decision: {status!r}")
                await ctx.send_message({**message,"phase":"effect_resolved"})
        class Ack(Executor):
            @handler
            async def process(self,message:dict,ctx:WorkflowContext[dict])->None:
                FileLedger(Path(message["ledger_path"])).ack(); trace.append("ack"); await ctx.send_message({**message,"phase":"acked"})
        class End(Executor):
            @handler
            async def process(self,message:dict,ctx:WorkflowContext[Never,dict])->None:
                FileLedger(Path(message["ledger_path"])).finish(); trace.append("finish"); await ctx.yield_output({**message,"phase":"finished"})
        a=Guard(id="effect_guard"); b=Ack(id="ack"); z=End(id="finish"); wb=WorkflowBuilder(name=f"reva-target-{Path(run_dir).name}",start_executor=a); wb.add_edge(a,b); wb.add_edge(b,z); wf=wb.build(); output=None
        async for e in wf.run(message={"ledger_path":str(ledger),"effect_status":effect_status,"phase":"resume"},stream=True):
            if getattr(e,"type",None)=="output": output=getattr(e,"data",None)
        return {"ledger":FileLedger(ledger).read(),"effect_decision":trace[0] if trace else "","trace":trace,"native_kind":"maf_target_workflow","result":output}
    def run_from_effect_decision(self,effect_status,run_dir): return asyncio.run(self._target_async(effect_status,run_dir))
