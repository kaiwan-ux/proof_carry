# No future annotations: agent-framework validates WorkflowContext annotations at registration time.
import asyncio
from typing import Any
from typing_extensions import Never
from ..models import RuntimeState
from ..semantics import continue_case
class MAFAgentAdapter:
    name="maf"
    def run_target(self,family,state,ledger):
        async def _run():
            from agent_framework import Executor,InMemoryCheckpointStorage,WorkflowBuilder,WorkflowContext,handler
            try: from typing import override
            except ImportError: from typing_extensions import override
            class Start(Executor):
                @handler
                async def process(self,message:dict,ctx:WorkflowContext[dict])->None: await ctx.send_message(message)
            class Work(Executor):
                def __init__(self,id:str): super().__init__(id=id); self.last={}
                @handler
                async def process(self,message:dict,ctx:WorkflowContext[dict])->None:
                    s=RuntimeState.from_dict(message["logical"]); ld=dict(message.get("ledger",{})); out,ld=continue_case(family,s,ld); self.last={"logical":out.to_dict(),"ledger":ld}; await ctx.send_message(self.last)
                @override
                async def on_checkpoint_save(self)->dict[str,Any]: return {"last":self.last}
                @override
                async def on_checkpoint_restore(self,state:dict[str,Any])->None: self.last=dict((state or {}).get("last",{}))
            class End(Executor):
                @handler
                async def process(self,message:dict,ctx:WorkflowContext[Never,dict])->None: await ctx.yield_output(message)
            storage=InMemoryCheckpointStorage(); a=Start(id="start"); b=Work(id="resume"); c=End(id="end")
            wf=WorkflowBuilder(start_executor=a,checkpoint_storage=storage).add_edge(a,b).add_edge(b,c).build(); output=None; events=[]
            async for e in wf.run(message={"logical":state.to_dict(),"ledger":dict(ledger)},stream=True):
                events.append(getattr(e,"type",type(e).__name__))
                if getattr(e,"type",None)=="output": output=e.data
            if output is None: raise RuntimeError("MAF produced no output")
            cps=await storage.list_checkpoints(workflow_name=wf.name)
            return output,{"kind":"maf_workflow_checkpoint","workflow_name":wf.name,"checkpoint_count":len(cps),"events":events}
        out,native=asyncio.run(_run()); ledger.clear(); ledger.update(out["ledger"]); return RuntimeState.from_dict(out["logical"]),native
