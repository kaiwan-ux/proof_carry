from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/'results'
for p in R.iterdir():
    if p.name in {'semantic','native','probes','graphs','artifacts'}:
        shutil.rmtree(p,ignore_errors=True); p.mkdir(parents=True,exist_ok=True); (p/'.gitkeep').write_text('')
    elif p.is_file(): p.unlink()
print('results cleaned')
