import json
from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt,Command
from typing import TypedDict
class S(TypedDict,total=False): count:int
count={'effect':0}
def n(s:S): count['effect']+=1; interrupt('approve'); return {'count':count['effect']}
b=StateGraph(S); b.add_node('n',n); b.add_edge(START,'n'); b.add_edge('n',END); g=b.compile(checkpointer=InMemorySaver()); cfg={'configurable':{'thread_id':'crb-probe'}}
try: g.invoke({'count':0},cfg)
except Exception: pass
before=count['effect']
try: g.invoke(Command(resume=True),cfg)
except Exception: pass
print(json.dumps({'framework':'langgraph','effect_before_resume':before,'effect_after_resume':count['effect'],'reentered_node':count['effect']>before}))
