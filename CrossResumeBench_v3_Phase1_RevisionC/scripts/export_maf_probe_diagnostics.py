from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
out = ROOT / "CrossResumeBench_v3_Phase1_RevisionC_MAF_probe_diagnostics.zip"
include = [
    RES / "MAF_REVISIONC_PROBE.json",
    RES / "capabilities.json",
]
manifest = {}
for p in include:
    if p.exists():
        manifest[str(p.relative_to(ROOT))] = hashlib.sha256(p.read_bytes()).hexdigest()
manifest_path = RES / "MAF_PROBE_DIAGNOSTIC_MANIFEST.json"
manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for p in include + [manifest_path]:
        if p.exists():
            z.write(p, p.relative_to(ROOT))
print(out)
