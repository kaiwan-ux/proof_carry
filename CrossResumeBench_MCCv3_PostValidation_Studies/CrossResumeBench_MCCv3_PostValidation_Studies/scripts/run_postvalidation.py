from __future__ import annotations
from _bootstrap import *
import argparse, json, shutil
from pathlib import Path
from studies.common import ROOT, verify_passed_holdout_inputs
from studies.statistics.paired_analysis import run as run_stats
from studies.ablation.run_ablation import run as run_ablation
from studies.performance.run_microbench import run as run_micro

def main(out:Path,bootstrap_reps=10000,micro_repeats=10):
    verify_passed_holdout_inputs();shutil.rmtree(out,ignore_errors=True);out.mkdir(parents=True)
    results={}
    results['statistics']=run_stats(out/'statistics',bootstrap_reps)
    results['ablation']=run_ablation(out/'ablation')
    m=run_micro(out/'performance_micro',micro_repeats,2);results['performance_micro']={'instances':m['instances_per_repeat'],'repeats':m['repeats']}
    (out/'POSTVALIDATION_SUMMARY.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    return results
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',default=str(ROOT/'results'));ap.add_argument('--bootstrap-reps',type=int,default=10000);ap.add_argument('--micro-repeats',type=int,default=10);a=ap.parse_args();print(json.dumps(main(Path(a.out),a.bootstrap_reps,a.micro_repeats),indent=2))
