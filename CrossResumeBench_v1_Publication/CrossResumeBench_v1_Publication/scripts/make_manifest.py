from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/'results'; entries=[]
for p in sorted(R.rglob('*')):
    if p.is_file() and p.name not in {'MANIFEST.json','CHECKSUMS_SHA256.txt'}:
        entries.append({'path':str(p.relative_to(R)).replace('\\','/'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
(R/'MANIFEST.json').write_text(json.dumps(entries,indent=2),encoding='utf-8'); (R/'CHECKSUMS_SHA256.txt').write_text(''.join(f"{x['sha256']}  {x['path']}\n" for x in entries),encoding='utf-8'); print('manifest',len(entries))
