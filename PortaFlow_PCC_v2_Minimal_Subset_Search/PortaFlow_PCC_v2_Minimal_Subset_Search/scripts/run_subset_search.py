from pathlib import Path
import csv,json
from collections import defaultdict
from portaflow_min.search import exhaustive_rows, pareto, choose_minimal
from portaflow_min.components import COMPONENTS
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/'results'
rows=exhaustive_rows()
with (R/'subset_workflow_results.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].to_dict())); w.writeheader(); w.writerows([x.to_dict() for x in rows])
# aggregate
agg={}
for x in rows:
    k=(x.inference_mode,x.subset_key,x.components,x.component_count)
    a=agg.setdefault(k,{'inference_mode':x.inference_mode,'subset_key':x.subset_key,'components':x.components,'component_count':x.component_count,'cases':0,'safe_completions':0,'rejections':0,'unsafe_violations':0,'bytes':[]})
    a['cases']+=1; a['safe_completions']+=x.safe_completion; a['rejections']+=x.migration_rejected; a['unsafe_violations']+=x.unsafe_violation; a['bytes'].append(x.capsule_bytes)
aggregates=[]
for a in agg.values():
    b={k:v for k,v in a.items() if k!='bytes'}; b['safe_rate']=b['safe_completions']/b['cases']; b['rejection_rate']=b['rejections']/b['cases']; b['unsafe_rate']=b['unsafe_violations']/b['cases']; b['mean_capsule_bytes']=sum(a['bytes'])/len(a['bytes']); aggregates.append(b)
aggregates=sorted(aggregates,key=lambda x:(x['inference_mode'],x['component_count'],x['subset_key']))
with (R/'subset_summary.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(aggregates[0])); w.writeheader(); w.writerows(aggregates)
front=pareto(aggregates)
with (R/'pareto_frontier.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(front[0])); w.writeheader(); w.writerows(front)
hexp=choose_minimal(aggregates,'explicit'); hhyb=choose_minimal(aggregates,'hybrid')
obj={'explicit_minimal':hexp,'hybrid_minimal':hhyb,'component_vocabulary':list(COMPONENTS),'search_space_size':64,'workflow_count':8}
(R/'minimal_candidates.json').write_text(json.dumps(obj,indent=2),encoding='utf-8')
# Select a compact native confirmation set. Names are semantic, component choices come from search output.
def parts(row): return [] if row is None or row['subset_key']=='none' else row['subset_key'].split('+')
selected=[]
def add(name,comps,mode,purpose):
    key=(tuple(comps),mode)
    if any((tuple(x['components']),x['inference_mode'])==key for x in selected): return
    selected.append({'name':name,'components':list(comps),'inference_mode':mode,'purpose':purpose})
add('state_only',[],'explicit','negative control')
add('raw_history',['history'],'explicit','history without inference')
add('history_inference',['history'],'hybrid','strong reconstruction baseline')
add('receipts_only',['receipts'],'explicit','tests receipt sufficiency without reconstructable trace')
if hhyb: add('hybrid_minimal',parts(hhyb),'hybrid','smallest full-coverage zero-unsafe hybrid subset discovered in Stage A')
if hexp: add('explicit_minimal',parts(hexp),'explicit','smallest full-coverage zero-unsafe explicit subset discovered in Stage A')
add('full_pcc',list(COMPONENTS),'explicit','full reference representation')
# add immediate ablations of hybrid minimal to verify native necessity
if hhyb:
    hp=parts(hhyb)
    for c in hp: add(f'hybrid_minimal_minus_{c}',[x for x in hp if x!=c],'hybrid','one-component ablation of Stage-A minimal candidate')
(R/'selected_native_conditions.json').write_text(json.dumps(selected,indent=2),encoding='utf-8')
print(json.dumps({'minimal_candidates':obj,'selected_native_conditions':selected},indent=2))
