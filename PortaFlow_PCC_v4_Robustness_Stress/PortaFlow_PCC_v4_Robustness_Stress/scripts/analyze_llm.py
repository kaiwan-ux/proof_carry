from pathlib import Path
import pandas as pd,json
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'results';p=R/'llm'/'llm_robustness_runs.csv'
if not p.exists():raise SystemExit('Run optional LLM stage first.')
d=pd.read_csv(p); d['technical']=(d.action=='TECHNICAL_FAILURE').astype(int)
s=d.groupby(['condition','profile']).agg(rows=('case','count'),accepted=('accepted','sum'),correct=('correct','sum'),technical=('technical','sum')).reset_index();s['accuracy']=s.correct/s.rows;s.to_csv(R/'llm'/'llm_robustness_summary.csv',index=False)
(R/'llm'/'LLM_VERDICT.json').write_text(json.dumps({'model':str(d.model.iloc[0]),'rows':len(d),'technical_failures':int(d.technical.sum()),'summary':s.to_dict(orient='records'),'note':'Secondary stochastic/LLM robustness evidence; deterministic native experiment remains primary.'},indent=2),encoding='utf-8');print(s.to_string(index=False))
