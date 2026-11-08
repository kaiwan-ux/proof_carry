from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]; RES=ROOT/'results'
for p in RES.iterdir():
    if p.name == 'README.md': continue
    if p.is_dir():
        shutil.rmtree(p)
    else: p.unlink()
for d in ['graphs','native_sources','native_targets','capsules','probes']:
    (RES/d).mkdir(parents=True,exist_ok=True)
    (RES/d/'.gitkeep').write_text('',encoding='utf-8')
print('Clean results ready.')
