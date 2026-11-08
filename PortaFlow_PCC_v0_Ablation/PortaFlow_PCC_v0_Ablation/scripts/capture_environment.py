from pathlib import Path
import json, platform, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]; RES=ROOT/'results'
try:
    freeze=subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True,encoding='utf-8',errors='replace')
except Exception as e: freeze=f'pip freeze failed: {e}'
(RES/'ENVIRONMENT.json').write_text(json.dumps({'python':sys.version,'platform':platform.platform()},indent=2),encoding='utf-8')
(RES/'PIP_FREEZE.txt').write_text(freeze,encoding='utf-8')
print('Environment captured.')
