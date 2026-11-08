from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]; RES=ROOT/'results'; OUT=ROOT/'PortaFlow_PCC_v0_results.zip'
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(RES.rglob('*')):
        if p.is_file() and p.name!='.gitkeep': z.write(p,arcname=f'results/{p.relative_to(RES)}')
print(OUT)
