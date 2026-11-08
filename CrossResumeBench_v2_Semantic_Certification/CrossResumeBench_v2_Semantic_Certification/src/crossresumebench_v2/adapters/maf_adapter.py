# No future annotations: Agent Framework validates handler annotations.
import asyncio
from typing import Any
from typing_extensions import Never
from ..source_engine import init_source,apply_source_action,finalize_source
from ..target_engine import init_target,apply_target_action,finalize_target

class MAFAdapter:
    name="maf"
    def capture_source(self,case):
        async def go():
            from agent_framework import Executor,InMemoryCheckpointStorage,WorkflowBuilder,WorkflowContext,handler
            class ActionExecutor(Executor):
                def __init__(self,id,action): super().__init__(id=id); self.action=action; self.last={}
                @handler
                async def process(self,message:dict,ctx:WorkflowContext[dict])->None:
                    state=dict(message.get("ctx") or init_source(case)); apply_source_action(state,self.action,case); self.last=state; await ctx.send_message({"ctx":state})
                async def on_checkpoint_save(self)->dict[str,Any]: return {"last":self.last}
                async def on_checkpoint_restore(self,state:dict[str,Any])->None: self.last=dict((state or {}).get("last",{}))
            class End(Executor):
                @handler
                async def process(self,message:dict,ctx:WorkflowContext[Never,dict])->None: await ctx.yield_output(message)
            storage=InMemoryCheckpointStorage(); acts=[ActionExecutor(f"src{i}",a) for i,a in enumerate(case.source_actions)]; z=End(id="end")
            builder=WorkflowBuilder(start_executor=acts[0],checkpoint_storage=storage)
            for a,b in zip(acts,acts[1:]): builder.add_edge(a,b)
            builder.add_edge(acts[-1],z); wf=builder.build(); out=None
            async for e in wf.run(message={"ctx":init_source(case)},stream=True):
                if getattr(e,"type",None)=="output": out=e.data
            cps=await storage.list_checkpoints(workflow_name=wf.name); obs={"kind":"maf_workflow_checkpoint","framework":"maf","real_native":True,"workflow_name":wf.name,"checkpoint_count":len(cps),"native_action_executors":len(acts)}
            return finalize_source(out["ctx"],case,obs)
        return asyncio.run(go())
    def run_target(self,case,continuation,ledger):
        async def go():
            from agent_framework import Executor,InMemoryCheckpointStorage,WorkflowBuilder,WorkflowContext,handler
            class ActionExecutor(Executor):
                def __init__(self,id,action): super().__init__(id=id); self.action=action; self.last={}
                @handler
                async def process(self,message:dict,ctx:WorkflowContext[dict])->None:
                    state=dict(message["ctx"]); apply_target_action(state,self.action); self.last=state; await ctx.send_message({"ctx":state})
                async def on_checkpoint_save(self)->dict[str,Any]: return {"last":self.last}
                async def on_checkpoint_restore(self,state:dict[str,Any])->None: self.last=dict((state or {}).get("last",{}))
            class End(Executor):
                @handler
                async def process(self,message:dict,ctx:WorkflowContext[Never,dict])->None: await ctx.yield_output(message)
            storage=InMemoryCheckpointStorage(); acts=[ActionExecutor(f"tgt{i}",a) for i,a in enumerate(case.target_actions)]; z=End(id="end")
            builder=WorkflowBuilder(start_executor=acts[0],checkpoint_storage=storage)
            for a,b in zip(acts,acts[1:]): builder.add_edge(a,b)
            builder.add_edge(acts[-1],z); wf=builder.build(); out=None
            async for e in wf.run(message={"ctx":init_target(continuation,ledger)},stream=True):
                if getattr(e,"type",None)=="output": out=e.data
            cps=await storage.list_checkpoints(workflow_name=wf.name)
            return finalize_target(out["ctx"],{"kind":"maf_workflow_checkpoint","framework":"maf","real_native":True,"workflow_name":wf.name,"checkpoint_count":len(cps),"native_action_executors":len(acts)})
        return asyncio.run(go())
