from __future__ import annotations
from typing import TypedDict,Any
from ..models import RuntimeState
from ..semantics import continue_case
class LGState(TypedDict,total=False): logical:dict[str,Any]; ledger:dict[str,int]
class LangGraphAdapter:
    name="langgraph"
    def run_target(self,family,state,ledger):
        from langgraph.graph import StateGraph,START,END
        from langgraph.checkpoint.memory import InMemorySaver
        def work(st:LGState):
            s=RuntimeState.from_dict(st["logical"]); ld=dict(st.get("ledger",{})); out,ld=continue_case(family,s,ld); return {"logical":out.to_dict(),"ledger":ld}
        b=StateGraph(LGState); b.add_node("resume_semantics",work); b.add_edge(START,"resume_semantics"); b.add_edge("resume_semantics",END)
        cp=InMemorySaver(); g=b.compile(checkpointer=cp); cfg={"configurable":{"thread_id":f"crb-{state.case_id}-{id(state)}"}}
        fin=g.invoke({"logical":state.to_dict(),"ledger":dict(ledger)},cfg); ledger.clear(); ledger.update(fin["ledger"]); snap=g.get_state(cfg)
        return RuntimeState.from_dict(fin["logical"]),{"kind":"langgraph_checkpoint","next":list(snap.next),"values_keys":sorted(snap.values.keys()),"config":dict(snap.config)}
