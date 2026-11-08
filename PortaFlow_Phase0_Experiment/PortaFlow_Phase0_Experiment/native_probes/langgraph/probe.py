from __future__ import annotations

import json
from typing import TypedDict


def main() -> None:
    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.graph import END, START, StateGraph
    from langgraph.types import Command, interrupt

    class S(TypedDict, total=False):
        completed: list[str]
        value: int

    def node(name: str):
        def fn(state: S):
            return {"completed": list(state.get("completed", [])) + [name], "value": int(state.get("value", 0)) + 1}
        return fn

    cp = InMemorySaver()
    b = StateGraph(S)
    for n in ("A","B","C"):
        b.add_node(n, node(n))
    b.add_edge(START,"A"); b.add_edge("A","B"); b.add_edge("B","C"); b.add_edge("C",END)
    g = b.compile(checkpointer=cp)
    cfg={"configurable":{"thread_id":"pf-lg-linear"}}
    full=g.invoke({"completed":[],"value":0}, cfg)
    hist=list(g.get_state_history(cfg))
    before_c=next((x for x in hist if tuple(x.next)==("C",)), None)
    resumed=None
    if before_c is not None:
        resumed=g.invoke(None, before_c.config)

    effect={"count":0}
    class I(TypedDict, total=False):
        approved: bool

    def approval_node(state: I):
        # Deliberate non-idempotent external effect before interrupt to expose re-entry semantics.
        effect["count"] += 1
        ok=interrupt({"question":"approve?"})
        return {"approved": bool(ok)}

    cp2=InMemorySaver(); b2=StateGraph(I); b2.add_node("approval",approval_node); b2.add_edge(START,"approval"); b2.add_edge("approval",END)
    gi=b2.compile(checkpointer=cp2); cfg2={"configurable":{"thread_id":"pf-lg-interrupt"}}
    first=gi.invoke({},cfg2)
    count_after_pause=effect["count"]
    second=gi.invoke(Command(resume=True),cfg2)
    count_after_resume=effect["count"]

    payload={
        "framework":"langgraph",
        "status":"ok",
        "probe":"checkpoint_and_interrupt",
        "linear":{
            "full":full,
            "checkpoint_count":len(hist),
            "selected_before_c": bool(before_c),
            "selected_next": list(before_c.next) if before_c else None,
            "selected_values": dict(before_c.values) if before_c else None,
            "resume_result": resumed,
        },
        "interrupt":{
            "effect_count_after_pause":count_after_pause,
            "effect_count_after_resume":count_after_resume,
            "reentered_node":count_after_resume>count_after_pause,
            "first_result":str(first),
            "resume_result":second,
        }
    }
    print(json.dumps(payload, default=str))

if __name__=="__main__":
    main()
