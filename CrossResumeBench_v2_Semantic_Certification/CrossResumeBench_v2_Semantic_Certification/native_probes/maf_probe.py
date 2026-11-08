import json
try:
 from agent_framework import InMemoryCheckpointStorage
 print(json.dumps({'status':'ok','capability':'workflow_checkpoint','package':'agent-framework-core'}))
except Exception as e: print(json.dumps({'status':'error','error':str(e)})); raise
