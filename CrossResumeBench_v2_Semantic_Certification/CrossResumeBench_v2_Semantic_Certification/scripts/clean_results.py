from pathlib import Path
import shutil
R=Path(__file__).resolve().parents[1]/'results'
for p in R.iterdir():
    if p.name in {'artifacts','native_sources','native_targets','graphs','probes'}:
        shutil.rmtree(p,ignore_errors=True); p.mkdir(parents=True,exist_ok=True); (p/'.gitkeep').write_text('')
    elif p.is_file(): p.unlink()
print('results cleaned')
