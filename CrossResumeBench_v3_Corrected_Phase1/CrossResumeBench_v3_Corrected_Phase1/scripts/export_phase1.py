from pathlib import Path
import zipfile,json
ROOT=Path(__file__).resolve().parents[1]
g=json.loads((ROOT/'results/PHASE1_GATE.json').read_text())
if not g.get('go_for_full_v3'): raise SystemExit('Refusing to export a success package because the Phase 1 gate did not pass.')
out=ROOT/'CrossResumeBench_v3_Phase1_results.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for p in (ROOT/'results').rglob('*'):
        if p.is_file() and 'work' not in p.parts: z.write(p,p.relative_to(ROOT))
print(out)
