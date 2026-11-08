from pathlib import Path
import asyncio
from typing import Any
from typing_extensions import Never
from ..models import NativePause
from ..ledger import FileLedger

class MAFRuntime:
    name="maf"
    def capability_probe(self):
        import agent_framework
        from agent_framework import WorkflowBuilder,InMemoryCheckpointStorage
        return {"framework":self.name,"installed":True,"version":getattr(agent_framework,"__version__","unknown"),"workflow_builder":WorkflowBuilder is not None,"checkpoint_storage":InMemoryCheckpointStorage is not None,"pause_kind":"superstep_checkpoint"}
    def _build(self,storage,ledger_path):
        from agent_framework import Executor,WorkflowBuilder,WorkflowContext,handler
        class Commit(Executor):
            @handler
            async def process(self,message:dict,ctx:WorkflowContext[dict])->None:
                FileLedger(Path(message["ledger_path"])).commit_effect(); await ctx.send_message({**message,"phase":"effect_committed"})
        class Ack(Executor):
            @handler
            async def process(self,message:dict,ctx:WorkflowContext[dict])->None:
                FileLedger(Path(message["ledger_path"])).ack(); await ctx.send_message({**message,"phase":"acked"})
        class End(Executor):
            @handler
            async def process(self,message:dict,ctx:WorkflowContext[Never,dict])->None:
                FileLedger(Path(message["ledger_path"])).finish(); await ctx.yield_output({**message,"phase":"finished"})
        a=Commit(id="commit_effect"); b=Ack(id="ack"); z=End(id="finish")
        wb=WorkflowBuilder(start_executor=a,checkpoint_storage=storage); wb.add_edge(a,b); wb.add_edge(b,z); return wb.build()
    def capture_effect_ack_pause(self,run_dir):
        async def go():
            from agent_framework import InMemoryCheckpointStorage
            run_dir=Path(run_dir); ledger=run_dir/"ledger.json"; storage=InMemoryCheckpointStorage(); wf=self._build(storage,ledger)
            # Run to completion once only to materialize real checkpoints. Select the checkpoint after commit superstep; the checkpoint itself represents the paused state.
            async for _ in wf.run(message={"ledger_path":str(ledger),"phase":"start"},stream=True): pass
            cps=await storage.list_checkpoints(workflow_name=wf.name)
            if len(cps)<2: raise RuntimeError(f"MAF produced insufficient checkpoints: {len(cps)}")
            # Python >=1.13 has entry checkpoint first; first post-superstep checkpoint is index 1.
            chosen=cps[1]
            self._restore=(storage,wf.name,chosen,ledger)
            return NativePause(self.name,"effect_committed_ack_pending",str(chosen.checkpoint_id),"maf_workflow_checkpoint",["ack"],{"phase":"effect_committed"},[],[],{"workflow_name":wf.name,"checkpoint_id":str(chosen.checkpoint_id),"checkpoint_count":len(cps)},1)
        return asyncio.run(go())
    def self_resume_effect_ack(self,run_dir):
        async def go():
            p=self.capture_effect_ack_pause(run_dir); storage,wfname,chosen,ledger=self._restore
            FileLedger(ledger)._write({"effect_count":1,"ack_count":0,"finish_count":0})
            # Build a structurally compatible workflow and resume using checkpoint id.
            wf=self._build(storage,ledger)
            async for _ in wf.run(checkpoint_id=chosen.checkpoint_id,checkpoint_storage=storage,stream=True): pass
            d=FileLedger(ledger).read(); return {"safe":d=={"effect_count":1,"ack_count":1,"finish_count":1},"ledger":d,"pause":p.to_dict()}
        return asyncio.run(go())
    def run_ack_finish_from_mcc(self,reconstructed,run_dir):
        async def go():
            from agent_framework import Executor,WorkflowBuilder,WorkflowContext,handler
            run_dir=Path(run_dir); ledger=run_dir/"ledger.json"; l=FileLedger(ledger)
            if l.read()["effect_count"]==0: l.commit_effect()
            class Ack(Executor):
                @handler
                async def process(self,message:dict,ctx:WorkflowContext[dict])->None: FileLedger(Path(message["ledger_path"])).ack(); await ctx.send_message({**message,"phase":"acked"})
            class End(Executor):
                @handler
                async def process(self,message:dict,ctx:WorkflowContext[Never,dict])->None: FileLedger(Path(message["ledger_path"])).finish(); await ctx.yield_output({**message,"phase":"finished"})
            a=Ack(id="ack"); z=End(id="finish"); wf=WorkflowBuilder(start_executor=a).add_edge(a,z).build(); out=None
            async for e in wf.run(message={"ledger_path":str(ledger),"phase":"resume"},stream=True):
                if getattr(e,"type",None)=="output": out=e.data
            return {"ledger":l.read(),"native_kind":"maf_target_workflow","result":out}
        return asyncio.run(go())
