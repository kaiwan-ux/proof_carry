from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def run(*args):
    print('>',*args); subprocess.run([sys.executable,*args],cwd=ROOT,check=True)
run('scripts/verify_inputs.py')
run('studies/security/run_security_stress.py')
run('figures/scripts/generate_paper_figures.py')
run('scripts/verify_outputs.py')
run('scripts/export_results.py')
