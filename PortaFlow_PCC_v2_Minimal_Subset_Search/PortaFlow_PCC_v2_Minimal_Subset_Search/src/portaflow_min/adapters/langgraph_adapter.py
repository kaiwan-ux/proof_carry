from __future__ import annotations
from typing import TypedDict,Any
from ..models import ExecutionState,SourceCapture
from ..benchmark import initial_state,source_prefix_transition,continuation_transition
class LGState(TypedDict,total=False): logical:dict[str,Any]; ledger:dict[str,int]
def _snap(g,c):
    s=g.get_state(c); h=list(g.get_state_history(c)); return {"kind":"langgraph_checkpoint","values":dict(s.values),"next":list(s.next),"tasks":[str(x) for x in s.tasks],"checkpoint_count":len(h),"config":dict(s.config)}
def run_source(workflow:str)->SourceCapture:
    from langgraph.graph import StateGraph,START,END
    from langgraph.checkpoint.memory import InMemorySaver
    def node(st:LGState):
        s=ExecutionState.from_dict(st["logical"]); ld=dict(st.get("ledger",{})); out=source_prefix_transition(s,ld); return {"logical":out.to_dict(),"ledger":ld}
    b=StateGraph(LGState); b.add_node("prefix",node); b.add_edge(START,"prefix"); b.add_edge("prefix",END); cp=InMemorySaver(); g=b.compile(checkpointer=cp); cfg={"configurable":{"thread_id":f"min-src-{workflow}"}}
    fin=g.invoke({"logical":initial_state(workflow).to_dict(),"ledger":{}},cfg); return SourceCapture("langgraph",workflow,fin["logical"],_snap(g,cfg),dict(fin["ledger"]))
def run_target(workflow:str,imported:ExecutionState,ledger:dict[str,int]):
    from langgraph.graph import StateGraph,START,END
    from langgraph.checkpoint.memory import InMemorySaver
    def node(st:LGState):
        s=ExecutionState.from_dict(st["logical"]); ld=dict(st.get("ledger",{})); out=continuation_transition(s,ld); return {"logical":out.to_dict(),"ledger":ld}
    b=StateGraph(LGState); b.add_node("continue",node); b.add_edge(START,"continue"); b.add_edge("continue",END); cp=InMemorySaver(); g=b.compile(checkpointer=cp); cfg={"configurable":{"thread_id":f"min-tgt-{workflow}-{id(imported)}"}}
    fin=g.invoke({"logical":imported.to_dict(),"ledger":dict(ledger)},cfg); ledger.clear(); ledger.update(fin["ledger"]); return ExecutionState.from_dict(fin["logical"]),_snap(g,cfg)
