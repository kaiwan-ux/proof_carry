from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/'results'
if R.exists(): shutil.rmtree(R)
for d in ['graphs','capsules','inference_reports','native_sources','native_targets','probes','llm']:(R/d).mkdir(parents=True,exist_ok=True)
print('Clean results directory created.')
