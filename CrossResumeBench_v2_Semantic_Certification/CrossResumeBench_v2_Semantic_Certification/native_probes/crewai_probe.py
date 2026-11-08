import json
try:
 from crewai.flow.flow import Flow,start
 print(json.dumps({'status':'ok','capability':'flow_state','package':'crewai'}))
except Exception as e: print(json.dumps({'status':'error','error':str(e)})); raise
