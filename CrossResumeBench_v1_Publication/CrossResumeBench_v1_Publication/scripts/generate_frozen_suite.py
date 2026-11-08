# DEVELOPMENT ONLY: do not run on the frozen v1 benchmark after observing results. Use only when creating a new version.
from pathlib import Path
import json,hashlib
from crossresumebench.generator import generate_suite
ROOT=Path(__file__).resolve().parents[1]
cases=generate_suite(260826,5); path=ROOT/'benchmark/generated_suite.json'; path.write_text(json.dumps([c.to_dict() for c in cases],indent=2),encoding='utf-8')
d=hashlib.sha256(path.read_bytes()).hexdigest(); (ROOT/'benchmark/FROZEN_SUITE_SHA256.txt').write_text(d+'\n',encoding='utf-8'); print('cases',len(cases),'suite SHA256',d)
