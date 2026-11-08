from __future__ import annotations
from typing import TypedDict, Any
from ..source_engine import init_source, apply_source_action, finalize_source
from ..target_engine import init_target, apply_target_action, finalize_target

class LGState(TypedDict, total=False):
    ctx: dict[str, Any]

class LangGraphAdapter:
    name = "langgraph"

    def capture_source(self, case):
        from langgraph.graph import StateGraph, START, END
        from langgraph.checkpoint.memory import InMemorySaver
        b = StateGraph(LGState)
        names=[]
        for i, raw in enumerate(case.source_actions):
            name=f"src_{i}_{raw['action_id']}"; names.append(name)
            def make_node(action):
                def node(st):
                    ctx = dict(st.get("ctx") or init_source(case))
                    apply_source_action(ctx, action, case)
                    return {"ctx": ctx}
                return node
            b.add_node(name, make_node(raw))
        if names:
            b.add_edge(START, names[0])
            for a, z in zip(names, names[1:]): b.add_edge(a, z)
            b.add_edge(names[-1], END)
        cp=InMemorySaver(); g=b.compile(checkpointer=cp); cfg={"configurable":{"thread_id":f"crb2-src-{case.case_id}"}}
        out=g.invoke({"ctx":init_source(case)},cfg); snap=g.get_state(cfg)
        obs={"kind":"langgraph_checkpoint","framework":"langgraph","real_native":True,"next":list(snap.next),"values_keys":sorted(snap.values.keys()),"config":dict(snap.config),"native_action_nodes":len(names)}
        return finalize_source(out["ctx"],case,obs)

    def run_target(self, case, continuation, ledger):
        from langgraph.graph import StateGraph, START, END
        from langgraph.checkpoint.memory import InMemorySaver
        b=StateGraph(LGState); names=[]
        for i, raw in enumerate(case.target_actions):
            name=f"tgt_{i}_{raw['action_id']}"; names.append(name)
            def make_node(action):
                def node(st):
                    ctx=dict(st["ctx"]); apply_target_action(ctx,action); return {"ctx":ctx}
                return node
            b.add_node(name,make_node(raw))
        b.add_edge(START,names[0])
        for a,z in zip(names,names[1:]): b.add_edge(a,z)
        b.add_edge(names[-1],END)
        cp=InMemorySaver(); g=b.compile(checkpointer=cp); cfg={"configurable":{"thread_id":f"crb2-tgt-{case.case_id}-{id(continuation)}"}}
        out=g.invoke({"ctx":init_target(continuation,ledger)},cfg); snap=g.get_state(cfg)
        return finalize_target(out["ctx"],{"kind":"langgraph_target_checkpoint","framework":"langgraph","real_native":True,"next":list(snap.next),"values_keys":sorted(snap.values.keys()),"native_action_nodes":len(names)})
