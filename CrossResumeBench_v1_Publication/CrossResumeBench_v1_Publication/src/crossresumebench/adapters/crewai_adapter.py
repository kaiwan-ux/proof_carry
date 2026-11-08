from __future__ import annotations
from typing import Any
from ..models import RuntimeState
from ..semantics import continue_case
class CrewAIAdapter:
    name="crewai"
    def run_target(self,family,state,ledger):
        from pydantic import BaseModel,Field
        from crewai.flow.flow import Flow,start
        class S(BaseModel): id:str=""; logical:dict[str,Any]=Field(default_factory=dict); ledger:dict[str,int]=Field(default_factory=dict)
        class F(Flow[S]):
            @start()
            def resume_semantics(self):
                s=RuntimeState.from_dict(self.state.logical); ld=dict(self.state.ledger); out,ld=continue_case(family,s,ld); self.state.logical=out.to_dict(); self.state.ledger=ld; return self.state.logical
        f=F(); f.kickoff(inputs={"logical":state.to_dict(),"ledger":dict(ledger)}); ledger.clear(); ledger.update(f.state.ledger)
        return RuntimeState.from_dict(f.state.logical),{"kind":"crewai_flow_state","flow_id":str(f.state.id),"state_keys":sorted(f.state.model_dump().keys())}
