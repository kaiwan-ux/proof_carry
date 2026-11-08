from __future__ import annotations
from typing import Any
from ..source_engine import init_source, apply_source_action, finalize_source
from ..target_engine import init_target, apply_target_action, finalize_target

class CrewAIAdapter:
    name="crewai"
    def capture_source(self,case):
        from pydantic import BaseModel,Field
        from crewai.flow.flow import Flow,start
        class S(BaseModel): id:str=""; ctx:dict[str,Any]=Field(default_factory=dict)
        class F(Flow[S]):
            @start()
            def run_source_actions(self):
                ctx=init_source(case)
                for raw in case.source_actions: apply_source_action(ctx,raw,case)
                self.state.ctx=ctx; return ctx
        f=F(); f.kickoff(); obs={"kind":"crewai_flow_state","framework":"crewai","real_native":True,"flow_id":str(f.state.id),"state_keys":sorted(f.state.model_dump().keys()),"native_action_count":len(case.source_actions)}
        return finalize_source(dict(f.state.ctx),case,obs)
    def run_target(self,case,continuation,ledger):
        from pydantic import BaseModel,Field
        from crewai.flow.flow import Flow,start
        class S(BaseModel): id:str=""; ctx:dict[str,Any]=Field(default_factory=dict)
        class F(Flow[S]):
            @start()
            def run_target_actions(self):
                ctx=init_target(continuation,ledger)
                for raw in case.target_actions: apply_target_action(ctx,raw)
                self.state.ctx=ctx; return ctx
        f=F(); f.kickoff(); return finalize_target(dict(f.state.ctx),{"kind":"crewai_flow_state","framework":"crewai","real_native":True,"flow_id":str(f.state.id),"state_keys":sorted(f.state.model_dump().keys()),"native_action_count":len(case.target_actions)})
