from __future__ import annotations
import csv,json
from pathlib import Path
def _read(p):
    with Path(p).open(encoding='utf-8') as f:return list(csv.DictReader(f))
def analyze(results):
    results=Path(results); rows=_read(results/'migration_runs.csv'); selfr=_read(results/'self_resume.csv'); srcr=_read(results/'source_captures.csv')
    def I(r,k): return int(r.get(k,0) or 0)
    methods=sorted({r['method'] for r in rows}); summary={}
    for m in methods:
        x=[r for r in rows if r['method']==m]; summary[m]={'rows':len(x),'safe_completion':sum(I(r,'safe_completion') for r in x),'safe_rejection':sum(I(r,'safe_rejection') for r in x),'unsafe':sum(I(r,'unsafe_violation') for r in x),'technical':sum(I(r,'technical_failure') for r in x)}
    v3=[r for r in rows if r['method']=='mcc_v3']; expected={}
    from .cases import CASE_BY_ID
    wrong_expected=0
    for r in v3:
        exp=CASE_BY_ID[r['case_id']].variant_expectations[r['evidence_variant']]; actual='safe_completion' if I(r,'safe_completion') else ('safe_rejection' if I(r,'safe_rejection') else ('unsafe' if I(r,'unsafe_violation') else 'technical'))
        if actual!=exp: wrong_expected+=1
    gate={'row_count_exact':len(rows)==6144,'self_rows_exact':len(selfr)==96,'source_rows_exact':len(srcr)==96,'zero_technical':sum(I(r,'technical_failure') for r in rows)==0,'mcc_v3_zero_unsafe':sum(I(r,'unsafe_violation') for r in v3)==0,'mcc_v3_matches_preregistered_expectations':wrong_expected==0,'native_self_resume_all':all(I(r,'self_resume_safe')==1 for r in selfr),'source_capture_all':all(I(r,'capture_success')==1 for r in srcr)}
    gate['go_for_mccv3_claims']=all(gate.values())
    verdict={'gate':gate,'methods':summary,'mcc_v3_rows':len(v3),'mcc_v3_expectation_mismatches':wrong_expected}
    (results/'RESEARCH_VERDICT.json').write_text(json.dumps(verdict,indent=2,sort_keys=True),encoding='utf-8')
    lines=['# MCC v3 Holdout Analysis','',f"**GO for MCC v3 claims:** {gate['go_for_mccv3_claims']}",'','## Gate']+[f"- {k}: {v}" for k,v in gate.items()]+['','## Methods']+[f"- {m}: {d}" for m,d in summary.items()]
    (results/'ANALYSIS_SUMMARY.md').write_text('\n'.join(lines)+'\n',encoding='utf-8'); return verdict
