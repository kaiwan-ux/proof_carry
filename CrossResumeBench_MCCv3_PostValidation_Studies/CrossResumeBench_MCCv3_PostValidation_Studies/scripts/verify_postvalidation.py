from _bootstrap import *
from pathlib import Path
import pandas as pd, json
from studies.common import ROOT, verify_passed_holdout_inputs

def main(root=ROOT/'results'):
    verify_passed_holdout_inputs();root=Path(root); problems=[]
    req=['statistics/method_summary.csv','statistics/paired_comparisons.json','statistics/STATISTICAL_REPORT.md','ablation/ablation_runs.csv','ablation/ablation_summary.csv','ablation/ABLATION_REPORT.md','performance_micro/microbench.json','performance_micro/MICROBENCH_REPORT.md','POSTVALIDATION_SUMMARY.json']
    for r in req:
        if not (root/r).exists():problems.append(f'missing {r}')
    if (root/'ablation/ablation_runs.csv').exists():
        df=pd.read_csv(root/'ablation/ablation_runs.csv')
        if len(df)!=5376:problems.append(f'ablation rows expected 5376 got {len(df)}')
        full=df[df.ablation=='full_mcc_v3']
        if len(full)!=768 or int(full.unsafe.sum())!=0:problems.append('full_mcc_v3 ablation control does not reproduce 768 rows / 0 unsafe')
    if problems: raise SystemExit('POSTVALIDATION VERIFY FAILED:\n- '+'\n- '.join(problems))
    print('POSTVALIDATION VERIFY PASS')
if __name__=='__main__':main()
