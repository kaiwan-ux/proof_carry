# No future annotations: agent-framework validates WorkflowContext at handler registration time.
import asyncio
from typing import Any
from typing_extensions import Never
from ..models import ExecutionState,SourceCapture
from ..benchmark import initial_state,source_prefix_transition,continuation_transition

def _se(e): return {"type":getattr(e,"type",type(e).__name__),"executor_id":getattr(e,"executor_id",None),"data":getattr(e,"data",None)}
async def _run(mode:str,logical:dict[str,Any],ledger:dict[str,int]):
    from agent_framework import Executor,InMemoryCheckpointStorage,WorkflowBuilder,WorkflowContext,handler
    try: from typing import override
    except ImportError: from typing_extensions import override
    class Start(Executor):
        @handler
        async def process(self,message:dict,ctx:WorkflowContext[dict])->None: await ctx.send_message(message)
    class Work(Executor):
        def __init__(self,id:str): super().__init__(id=id); self.last_state={}
        @handler
        async def process(self,message:dict,ctx:WorkflowContext[dict])->None:
            s=ExecutionState.from_dict(message["logical"]); ld=dict(message.get("ledger",{})); out=source_prefix_transition(s,ld) if mode=="source" else continuation_transition(s,ld); self.last_state={"logical":out.to_dict(),"ledger":ld}; await ctx.send_message(self.last_state)
        @override
        async def on_checkpoint_save(self)->dict[str,Any]: return {"last_state":self.last_state}
        @override
        async def on_checkpoint_restore(self,state:dict[str,Any])->None: self.last_state=dict((state or {}).get("last_state",{}))
    class End(Executor):
        @handler
        async def process(self,message:dict,ctx:WorkflowContext[Never,dict])->None: await ctx.yield_output(message)
    st=InMemoryCheckpointStorage(); a=Start(id="start"); b=Work(id="work"); c=End(id="end"); wf=WorkflowBuilder(start_executor=a,checkpoint_storage=st).add_edge(a,b).add_edge(b,c).build(); events=[]; output=None
    async for e in wf.run(message={"logical":logical,"ledger":ledger},stream=True):
        events.append(_se(e));
        if getattr(e,"type",None)=="output": output=e.data
    if output is None: raise RuntimeError("MAF produced no output")
    cps=await st.list_checkpoints(workflow_name=wf.name); latest=await st.get_latest(workflow_name=wf.name)
    return output,{"kind":"maf_workflow_checkpoint","workflow_name":wf.name,"checkpoint_count":len(cps),"events":events,"latest_checkpoint":latest.to_dict() if latest is not None and hasattr(latest,"to_dict") else None}
def run_source(workflow:str)->SourceCapture:
    out,snap=asyncio.run(_run("source",initial_state(workflow).to_dict(),{})); return SourceCapture("maf",workflow,dict(out["logical"]),snap,dict(out["ledger"]))
def run_target(workflow:str,imported:ExecutionState,ledger:dict[str,int]):
    out,snap=asyncio.run(_run("target",imported.to_dict(),dict(ledger))); ledger.clear(); ledger.update(out["ledger"]); return ExecutionState.from_dict(out["logical"]),snap
