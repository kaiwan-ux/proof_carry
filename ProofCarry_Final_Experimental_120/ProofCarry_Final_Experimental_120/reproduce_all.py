from __future__ import annotations
import argparse, json, shutil
from pathlib import Path
from proofcarry.utils import new_run_id, environment_snapshot, sha256_file
from experiments.run_expanded import run as run_expanded
from experiments.run_runtime_identity import run as run_runtime
from experiments.run_security import run as run_security
from experiments.run_ablation import run as run_ablation
from experiments.run_performance import run as run_perf
from experiments.analyze_sealed import run as run_sealed
from analysis.build_outputs import run as build_outputs
from scripts.audit_cases import audit as audit_cases
from native.run_native_validation import main as native_status

def main():
    ap=argparse.ArgumentParser(description='Reproduce ProofCarry final experiment suite.')
    ap.add_argument('--root',default=str(Path(__file__).resolve().parent))
    ap.add_argument('--run-id'); ap.add_argument('--seed',type=int,default=20260830)
    ap.add_argument('--performance-reps',type=int,default=30); ap.add_argument('--performance-warmups',type=int,default=5)
    ap.add_argument('--performance-max-cases',type=int,default=None)
    ap.add_argument('--skip-performance',action='store_true'); ap.add_argument('--native-status',action='store_true',help='Record dependency/native validation status; does not fabricate validation.')
    a=ap.parse_args(); root=Path(a.root).resolve(); run_id=a.run_id or new_run_id('proofcarry')
    raw=root/'results/raw'/run_id; proc=root/'results/processed'/run_id; raw.mkdir(parents=True,exist_ok=False)
    env=environment_snapshot(root); (raw/'environment.json').write_text(json.dumps(env,indent=2),encoding='utf-8')
    audit=audit_cases(root); (raw/'case_audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
    if not audit['pass']: raise SystemExit('Case audit failed; refusing to run.')
    run_sealed(root,raw/'sealed_summary.csv')
    run_expanded(root,raw/'expanded120.csv',run_id,a.seed)
    run_runtime(root,raw/'runtime_identity.csv',run_id,a.seed)
    run_security(root,raw/'security.csv',run_id,a.seed)
    run_ablation(root,raw/'ablation.csv',run_id,a.seed)
    if not a.skip_performance:
        run_perf(root,raw/'performance.csv',run_id,a.seed,a.performance_warmups,a.performance_reps,a.performance_max_cases)
    else:
        # Produce a tiny performance file so analysis can still run only if explicitly skipped? No: do not fabricate.
        raise SystemExit('--skip-performance currently stops before paper-output generation; run performance or analyze manually.')
    if a.native_status:
        native_status(root,root/'results/native'/f'{run_id}_native_validation.csv')
    build_outputs(root,raw,proc)
    (root/'results/LATEST_RUN.txt').write_text(run_id+'\n',encoding='utf-8')
    manifest={'run_id':run_id,'raw_dir':str(raw.relative_to(root)),'processed_dir':str(proc.relative_to(root)),'environment_sha256':sha256_file(raw/'environment.json')}
    (proc/'RUN_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps(manifest,indent=2))
if __name__=='__main__': main()
