from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]; RES=ROOT/'results'; OUT=ROOT/'PortaFlow_Corrected_results.zip'
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for p in sorted(RES.rglob('*')):
        if p.is_file(): z.write(p,p.relative_to(ROOT))
print(f'Wrote {OUT}')
