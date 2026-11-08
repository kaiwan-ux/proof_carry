from pathlib import Path
import json,datetime
ROOT=Path(__file__).resolve().parents[1]; rec=json.loads((ROOT/'benchmark'/'MECHANISM_FREEZE_RECORD.json').read_text()); rec['suite_hash']=(ROOT/'benchmark'/'FROZEN_SUITE_SHA256.txt').read_text().strip(); rec['suite_frozen_at']=datetime.datetime.now(datetime.timezone.utc).isoformat(); rec['order_verified']=rec['mechanism_frozen_at'] < rec['suite_frozen_at']; (ROOT/'benchmark'/'FREEZE_RECORD.json').write_text(json.dumps(rec,indent=2)); print(json.dumps(rec,indent=2))
