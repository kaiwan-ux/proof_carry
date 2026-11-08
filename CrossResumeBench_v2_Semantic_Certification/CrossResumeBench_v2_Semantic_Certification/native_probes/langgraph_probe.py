import json
try:
 from langgraph.graph import StateGraph,START,END
 from langgraph.checkpoint.memory import InMemorySaver
 class S(dict): pass
 print(json.dumps({'status':'ok','capability':'checkpoint','package':'langgraph'}))
except Exception as e: print(json.dumps({'status':'error','error':str(e)})); raise
