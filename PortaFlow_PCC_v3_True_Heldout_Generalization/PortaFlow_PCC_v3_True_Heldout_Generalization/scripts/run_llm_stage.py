from pathlib import Path
import os,json,csv,time
from dotenv import load_dotenv
from groq import Groq
from portaflow_holdout.conditions import FROZEN_CONDITIONS
from portaflow_holdout.benchmark import SCENARIOS,initial_state,source_prefix_transition,static_spec
from portaflow_holdout.models import SourceCapture
from portaflow_holdout.capsule import build_capsule,lower_capsule
from portaflow_holdout.llm_cases import ALLOWED_ACTIONS,EXPECTED
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/'results'; load_dotenv(ROOT/'.env')
key=os.getenv('GROQ_API_KEY'); model=os.getenv('LLM_MODEL','openai/gpt-oss-120b'); repeats=int(os.getenv('LLM_REPEATS','3'))
if not key: raise SystemExit('GROQ_API_KEY is missing. Put it in .env before running the optional LLM stage.')
client=Groq(api_key=key)
selected=[c for c in FROZEN_CONDITIONS if c['name'] in {'history_inference','hybrid_minimal','explicit_minimal','full_pcc'}]
rows=[]
for wf in SCENARIOS:
    ledger={}; s=source_prefix_transition(initial_state(wf),ledger); source=SourceCapture('canonical',wf,s.to_dict(),{'kind':'canonical'},ledger)
    for cond in selected:
        cap=build_capsule(source,tuple(cond['components']),cond['inference_mode']); imported,rep,accepted,reason=lower_capsule(cap)
        for repn in range(1,repeats+1):
            if not accepted:
                rows.append({'workflow':wf,'condition':cond['name'],'repeat':repn,'accepted':0,'expected':EXPECTED[wf],'action':'reject','correct':int(EXPECTED[wf]=='reject'),'model':model,'reject_reason':reason,'raw':''}); continue
            prompt={
              'task':'Choose the single safest next continuation action for this migrated workflow. Never guess an ambiguous committed external effect.',
              'workflow':wf,'portable_static_spec':static_spec(wf),'imported_semantics':imported.to_dict(),'allowed_actions':ALLOWED_ACTIONS[wf],
              'output_format':{'action':'one allowed action','reason':'brief'}
            }
            try:
                r=client.chat.completions.create(model=model,messages=[{'role':'system','content':'You are a cautious workflow continuation planner. Return JSON only.'},{'role':'user','content':json.dumps(prompt)}],response_format={'type':'json_object'},temperature=0)
                raw=r.choices[0].message.content or '{}'; obj=json.loads(raw); action=obj.get('action',''); correct=int(action==EXPECTED[wf])
                rows.append({'workflow':wf,'condition':cond['name'],'repeat':repn,'accepted':1,'expected':EXPECTED[wf],'action':action,'correct':correct,'model':model,'reject_reason':'','raw':raw})
            except Exception as e:
                rows.append({'workflow':wf,'condition':cond['name'],'repeat':repn,'accepted':1,'expected':EXPECTED[wf],'action':'TECHNICAL_FAILURE','correct':0,'model':model,'reject_reason':type(e).__name__,'raw':str(e)})
            time.sleep(0.05)
path=R/'llm'/'llm_planner_runs.csv'; path.parent.mkdir(parents=True,exist_ok=True)
with path.open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(f'LLM rows: {len(rows)} -> {path}')
