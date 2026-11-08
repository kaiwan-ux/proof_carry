from __future__ import annotations
from typing import TypedDict, Any
from ..models import LogicalState, SourceCapture
from ..scenarios import source_prefix_transition, continuation_transition

class LGState(TypedDict, total=False):
    logical: dict[str, Any]
    ledger: dict[str, int]


def _native_snapshot(graph, cfg) -> dict[str, Any]:
    snap=graph.get_state(cfg)
    hist=list(graph.get_state_history(cfg))
    return {
        "kind":"langgraph_checkpoint",
        "values":dict(snap.values),
        "next":list(snap.next),
        "tasks":[str(x) for x in snap.tasks],
        "checkpoint_count":len(hist),
        "config":dict(snap.config),
    }


def run_source(workflow: str) -> SourceCapture:
    from langgraph.graph import StateGraph, START, END
    from langgraph.checkpoint.memory import InMemorySaver
    initial=LogicalState(workflow=workflow,request_id=f"pf-{workflow}-001")
    ledger={}
    def prefix_node(st: LGState):
        s=LogicalState.from_dict(st["logical"]); ld=dict(st.get("ledger",{}))
        out=source_prefix_transition(s,ld)
        return {"logical":out.to_dict(),"ledger":ld}
    b=StateGraph(LGState); b.add_node("source_prefix",prefix_node); b.add_edge(START,"source_prefix"); b.add_edge("source_prefix",END)
    cp=InMemorySaver(); g=b.compile(checkpointer=cp); cfg={"configurable":{"thread_id":f"src-{workflow}"}}
    final=g.invoke({"logical":initial.to_dict(),"ledger":ledger},cfg)
    return SourceCapture("langgraph",workflow,final["logical"],_native_snapshot(g,cfg),dict(final["ledger"]))


def run_target(workflow: str, imported: LogicalState, ledger: dict[str,int]) -> tuple[LogicalState,dict[str,Any]]:
    from langgraph.graph import StateGraph, START, END
    from langgraph.checkpoint.memory import InMemorySaver
    def cont(st: LGState):
        s=LogicalState.from_dict(st["logical"]); ld=dict(st.get("ledger",{})); out=continuation_transition(s,ld)
        return {"logical":out.to_dict(),"ledger":ld}
    b=StateGraph(LGState); b.add_node("continuation",cont); b.add_edge(START,"continuation"); b.add_edge("continuation",END)
    cp=InMemorySaver(); g=b.compile(checkpointer=cp); cfg={"configurable":{"thread_id":f"tgt-{workflow}-{id(imported)}"}}
    final=g.invoke({"logical":imported.to_dict(),"ledger":dict(ledger)},cfg)
    ledger.clear(); ledger.update(final["ledger"])
    return LogicalState.from_dict(final["logical"]), _native_snapshot(g,cfg)
