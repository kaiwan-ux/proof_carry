import json,tempfile
from pathlib import Path
from crewai.flow.flow import Flow,start,listen
try:
    from crewai import CheckpointConfig
    supported=True
except Exception:
    supported=False
class F(Flow):
    @start()
    def a(self): self.state['a']=self.state.get('a',0)+1; return 'a'
    @listen(a)
    def b(self,_): self.state['b']=self.state.get('b',0)+1; return 'b'
kwargs={}
if supported: kwargs['checkpoint']=CheckpointConfig(location=str(Path(tempfile.mkdtemp())/'cp'),on_events=['method_execution_finished'])
f=F(**kwargs); f.kickoff(); print(json.dumps({'framework':'crewai','checkpoint_api_available':supported,'state':dict(f.state)}))
