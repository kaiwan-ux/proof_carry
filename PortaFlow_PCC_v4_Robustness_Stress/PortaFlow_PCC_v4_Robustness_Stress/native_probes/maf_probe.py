# No future-annotations import: MAF validates concrete WorkflowContext generic annotations.
import asyncio,json
from typing import Any
from typing_extensions import Never

async def amain():
    from agent_framework import Executor,InMemoryCheckpointStorage,WorkflowBuilder,WorkflowContext,handler
    try:
        from typing import override
    except ImportError:
        from typing_extensions import override

    class Start(Executor):
        @handler
        async def process(self,message:int,ctx:WorkflowContext[dict])->None:
            await ctx.send_message({"remaining":list(range(1,message+1))})

    class Worker(Executor):
        def __init__(self,id:str):
            super().__init__(id=id); self.seen=[]
        @handler
        async def process(self,message:dict,ctx:WorkflowContext[dict,str])->None:
            remaining=list(message.get("remaining",[]))
            n=remaining.pop(0); self.seen.append(n)
            if remaining:
                await ctx.send_message({"remaining":remaining})
            else:
                await ctx.yield_output("done:"+",".join(map(str,self.seen)))
        @override
        async def on_checkpoint_save(self)->dict[str,Any]:
            return {"seen":list(self.seen)}
        @override
        async def on_checkpoint_restore(self,state:dict[str,Any])->None:
            self.seen=list((state or {}).get("seen",[]))

    storage=InMemoryCheckpointStorage()
    start=Start(id="start"); worker=Worker(id="worker")
    builder=WorkflowBuilder(start_executor=start,checkpoint_storage=storage).add_edge(start,worker).add_edge(worker,worker)
    wf=builder.build(); first_events=[]; supersteps=0
    async for ev in wf.run(message=3,stream=True):
        first_events.append({"type":getattr(ev,"type",type(ev).__name__),"data":str(getattr(ev,"data",None))})
        if getattr(ev,"type",None)=="superstep_completed":
            supersteps += 1
            if supersteps>=2:
                break
    latest=await storage.get_latest(workflow_name=wf.name)
    if latest is None:
        raise RuntimeError("No MAF checkpoint produced before simulated interruption")

    # Rebuild fresh executor instances, then restore from the stored checkpoint.
    start2=Start(id="start"); worker2=Worker(id="worker")
    wf2=WorkflowBuilder(start_executor=start2).add_edge(start2,worker2).add_edge(worker2,worker2).build()
    resumed=[]; output=None
    async for ev in wf2.run(checkpoint_id=latest.checkpoint_id,checkpoint_storage=storage,stream=True):
        resumed.append({"type":getattr(ev,"type",type(ev).__name__),"data":str(getattr(ev,"data",None))})
        if getattr(ev,"type",None)=="output": output=str(getattr(ev,"data",None))
    cps=await storage.list_checkpoints(workflow_name=wf.name)
    print(json.dumps({"framework":"maf","status":"ok","checkpoint_count":len(cps),"selected_checkpoint":latest.to_dict() if hasattr(latest,"to_dict") else str(latest),"events_before_interrupt":first_events,"resume_events":resumed,"resume_output":output,"restored_worker_seen":worker2.seen},default=str))

def main(): asyncio.run(amain())
if __name__=="__main__": main()
