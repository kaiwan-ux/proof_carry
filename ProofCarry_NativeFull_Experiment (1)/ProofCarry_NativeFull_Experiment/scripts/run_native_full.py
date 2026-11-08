from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'frozen_v2'/'src'),str(ROOT)]
from crossresumebench_proofcarry.native_full_study import run_native_full, DEFAULT_VARIANTS

def main():
    ap=argparse.ArgumentParser(description='ProofCarry real native execution study')
    ap.add_argument('--out',default=None,help='result directory; default results/native_full_<timestamp>')
    ap.add_argument('--cases',choices=['smoke8','smoke24','paper104','all120'],default='all120')
    ap.add_argument('--profile',choices=['proofcarry','core','full'],default='proofcarry')
    ap.add_argument('--variants',default='all',help='all, enough, or comma-separated suite variant names')
    args=ap.parse_args()
    if args.out: out=ROOT/args.out
    else: out=ROOT/'results'/('native_full_'+time.strftime('%Y%m%d-%H%M%S'))
    if args.variants=='all': variants=DEFAULT_VARIANTS
    elif args.variants=='enough': variants=['enough_evidence']
    else: variants=[x.strip() for x in args.variants.split(',') if x.strip()]
    out.mkdir(parents=True,exist_ok=False)
    run_meta=run_native_full(out,case_preset=args.cases,profile=args.profile,variants=variants)
    (out/'NATIVE_RUN_META.json').write_text(json.dumps(run_meta,indent=2,sort_keys=True),encoding='utf-8')
    
    try: latest=str(out.relative_to(ROOT))
    except ValueError: latest=str(out)
    (ROOT/'results'/'LATEST_NATIVE_RUN.txt').write_text(latest,encoding='utf-8')
    print(json.dumps(run_meta,indent=2))
    print('RESULT_DIR=',out)
if __name__=='__main__': main()
