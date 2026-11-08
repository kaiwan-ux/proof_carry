from pathlib import Path
import pandas as pd,json
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/'results'; p=R/'llm'/'llm_planner_runs.csv'
if not p.exists(): raise SystemExit('Run scripts/run_llm_stage.py first.')
df=pd.read_csv(p); df['technical']=(df.action=='TECHNICAL_FAILURE').astype(int)
s=df.groupby('condition').agg(cases=('workflow','count'),correct=('correct','sum'),technical=('technical','sum')).reset_index(); s['accuracy']=s.correct/s.cases; s.to_csv(R/'llm'/'llm_summary.csv',index=False)
(R/'llm'/'LLM_VERDICT.json').write_text(json.dumps({'model':str(df.model.iloc[0]),'summary':s.to_dict(orient='records'),'claim_boundary':'LLM stage tests representation usefulness for continuation planning; it is not a pure framework-effect experiment.'},indent=2),encoding='utf-8')
print(s.to_string(index=False))
