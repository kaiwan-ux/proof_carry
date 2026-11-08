from __future__ import annotations
import json
from pathlib import Path
from .models import Case
ROOT=Path(__file__).resolve().parents[2]
SUITE=json.loads((ROOT/'benchmark'/'generated_suite.json').read_text(encoding='utf-8'))
CASES=[Case(**d) for d in SUITE['cases']]
CASE_BY_ID={c.case_id:c for c in CASES}
