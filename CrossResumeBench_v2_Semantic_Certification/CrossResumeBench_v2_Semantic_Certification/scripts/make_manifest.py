from pathlib import Path
import hashlib,json,datetime
ROOT=Path(__file__).resolve().parents[1]; files=[]
for p in sorted((ROOT/'results').rglob('*')):
    if p.is_file() and p.name not in {'MANIFEST.json','CHECKSUMS_SHA256.txt'}: files.append({'path':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
(ROOT/'results'/'MANIFEST.json').write_text(json.dumps({'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':files},indent=2)); (ROOT/'results'/'CHECKSUMS_SHA256.txt').write_text('\n'.join(f"{x['sha256']}  {x['path']}" for x in files)+'\n'); print(len(files),'manifested')
