from __future__ import annotations

import asyncio
import json


async def amain() -> None:
    from typing_extensions import Never
    from agent_framework import Executor, InMemoryCheckpointStorage, WorkflowBuilder, WorkflowContext, handler

    class MidStep(Executor):
        def __init__(self, id: str, label: str):
            super().__init__(id=id)
            self.label=label
            self.seen: list[str]=[]

        @handler
        async def process(self, message: str, ctx: WorkflowContext[str]) -> None:
            self.seen.append(str(message))
            ctx.set_executor_state({"label":self.label,"seen":list(self.seen)})
            await ctx.send_message(f"{message}->{self.label}")

        async def on_checkpoint_save(self) -> dict:
            return {"label":self.label,"seen":list(self.seen)}

        async def on_checkpoint_restore(self, state: dict) -> None:
            self.seen=list((state or {}).get("seen",[]))

    class EndStep(Executor):
        def __init__(self, id: str, label: str):
            super().__init__(id=id)
            self.label=label
            self.seen: list[str]=[]

        @handler
        async def process(self, message: str, ctx: WorkflowContext[Never, str]) -> None:
            self.seen.append(str(message))
            ctx.set_executor_state({"label":self.label,"seen":list(self.seen)})
            await ctx.yield_output(f"{message}->{self.label}")

        async def on_checkpoint_save(self) -> dict:
            return {"label":self.label,"seen":list(self.seen)}

        async def on_checkpoint_restore(self, state: dict) -> None:
            self.seen=list((state or {}).get("seen",[]))

    a=MidStep("a","A"); b=MidStep("b","B"); c=EndStep("c","C")
    storage=InMemoryCheckpointStorage()
    workflow=(WorkflowBuilder(start_executor=a, checkpoint_storage=storage)
              .add_edge(a,b).add_edge(b,c).build())

    events=[]
    async for event in workflow.run("start", stream=True):
        events.append({"type":getattr(event,"type",type(event).__name__),"executor_id":getattr(event,"executor_id",None),"data":str(getattr(event,"data",None))})

    checkpoints=await storage.list_checkpoints(workflow_name=workflow.name)
    cp_dicts=[x.to_dict() if hasattr(x,"to_dict") else {"checkpoint_id":getattr(x,"checkpoint_id",str(x))} for x in checkpoints]
    resumed_events=[]
    selected=None
    if len(checkpoints)>=2:
        selected=checkpoints[1]
        a2=MidStep("a","A"); b2=MidStep("b","B"); c2=EndStep("c","C")
        wf2=(WorkflowBuilder(start_executor=a2).add_edge(a2,b2).add_edge(b2,c2).build())
        async for event in wf2.run(checkpoint_id=selected.checkpoint_id, checkpoint_storage=storage, stream=True):
            resumed_events.append({"type":getattr(event,"type",type(event).__name__),"executor_id":getattr(event,"executor_id",None),"data":str(getattr(event,"data",None))})

    print(json.dumps({
        "framework":"maf","status":"ok","probe":"workflow_checkpoint",
        "workflow_name":workflow.name,
        "event_count":len(events),"events":events,
        "checkpoint_count":len(checkpoints),"checkpoints":cp_dicts,
        "selected_checkpoint_id":getattr(selected,"checkpoint_id",None),
        "resume_events":resumed_events,
    }, default=str))


def main() -> None:
    asyncio.run(amain())

if __name__=="__main__":
    main()
