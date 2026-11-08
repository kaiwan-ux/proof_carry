from pathlib import Path
import os,json,csv,time
from dotenv import load_dotenv
from groq import Groq
from portaflow_robust.conditions import FROZEN_CONDITIONS
from portaflow_robust.benchmark import SCENARIOS,split_case,initial_state,source_prefix_transition,static_spec
from portaflow_robust.models import SourceCapture
from portaflow_robust.capsule import build_capsule,lower_capsule
from portaflow_robust.llm_cases import actions_for,expected_for
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/'results'; load_dotenv(ROOT/'.env')
key=os.getenv('GROQ_API_KEY'); model=os.getenv('LLM_MODEL','openai/gpt-oss-120b'); repeats=int(os.getenv('LLM_REPEATS','5')); profiles=set(x.strip() for x in os.getenv('LLM_PROFILES','baseline,noise_duplicate,out_of_order').split(',') if x.strip())
if not key:raise SystemExit('GROQ_API_KEY missing. Copy .env.example to .env and add your key.')
client=Groq(api_key=key); selected=[c for c in FROZEN_CONDITIONS if c['name'] in {'history_inference','hybrid_minimal','explicit_minimal','full_pcc'}]; rows=[]
for case in SCENARIOS:
    base,profile=split_case(case)
    if profile not in profiles:continue
    ledger={}; s=source_prefix_transition(initial_state(case),ledger); source=SourceCapture('canonical',case,s.to_dict(),{'kind':'canonical'},ledger)
    for cond in selected:
        cap=build_capsule(source,tuple(cond['components']),cond['inference_mode']); imported,rep,accepted,reason=lower_capsule(cap)
        for repn in range(1,repeats+1):
            expected=expected_for(case)
            if not accepted:
                rows.append({'case':case,'base_workflow':base,'profile':profile,'condition':cond['name'],'repeat':repn,'accepted':0,'expected':expected,'action':'reject','correct':int(expected=='reject'),'model':model,'reject_reason':reason,'raw':''});continue
            prompt={'task':'Choose the single safest next continuation action. Do not replay committed irreversible effects. Reject if required evidence is genuinely unresolved.','case':case,'portable_static_spec':static_spec(case),'imported_semantics':imported.to_dict(),'allowed_actions':actions_for(case),'output_format':{'action':'one allowed action','reason':'brief'}}
            try:
                r=client.chat.completions.create(model=model,messages=[{'role':'system','content':'You are a cautious workflow continuation planner. Return JSON only.'},{'role':'user','content':json.dumps(prompt)}],response_format={'type':'json_object'},temperature=0)
                raw=r.choices[0].message.content or '{}'; obj=json.loads(raw); action=obj.get('action',''); rows.append({'case':case,'base_workflow':base,'profile':profile,'condition':cond['name'],'repeat':repn,'accepted':1,'expected':expected,'action':action,'correct':int(action==expected),'model':model,'reject_reason':'','raw':raw})
            except Exception as e: rows.append({'case':case,'base_workflow':base,'profile':profile,'condition':cond['name'],'repeat':repn,'accepted':1,'expected':expected,'action':'TECHNICAL_FAILURE','correct':0,'model':model,'reject_reason':type(e).__name__,'raw':str(e)})
            time.sleep(0.05)
path=R/'llm'/'llm_robustness_runs.csv'; path.parent.mkdir(parents=True,exist_ok=True)
with path.open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(f'LLM robustness rows: {len(rows)} -> {path}')
