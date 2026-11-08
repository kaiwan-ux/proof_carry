import json
from typing import TypedDict

def main():
    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.graph import START,END,StateGraph
    from langgraph.types import Command,interrupt
    class S(TypedDict,total=False): completed:list[str]
    effect={"count":0}
    def n1(s:S): return {"completed":list(s.get("completed",[]))+["A"]}
    def n2(s:S):
        effect["count"]+=1
        ok=interrupt({"question":"approve?"})
        return {"completed":list(s.get("completed",[]))+["B"]}
    b=StateGraph(S); b.add_node("A",n1); b.add_node("B",n2); b.add_edge(START,"A"); b.add_edge("A","B"); b.add_edge("B",END)
    cp=InMemorySaver(); g=b.compile(checkpointer=cp); cfg={"configurable":{"thread_id":"pf-probe"}}
    first=g.invoke({"completed":[]},cfg); before=effect["count"]; second=g.invoke(Command(resume=True),cfg); after=effect["count"]
    snap=g.get_state(cfg)
    print(json.dumps({"framework":"langgraph","status":"ok","effect_count_after_pause":before,"effect_count_after_resume":after,"reentered_node":after>before,"final":second,"snapshot":{"values":dict(snap.values),"next":list(snap.next)}},default=str))
if __name__=="__main__": main()
