from __future__ import annotations
import csv, json, os
from pathlib import Path
from datetime import datetime, timezone
from proofcarry.utils import sha256_obj, utc_now

def load_cases(root: Path):
    p=root/'benchmark/cases/all_cases.jsonl'
    return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]

def make_writer(path: Path, fieldnames):
    path.parent.mkdir(parents=True,exist_ok=True)
    f=path.open('w',newline='',encoding='utf-8')
    w=csv.DictWriter(f,fieldnames=fieldnames,extrasaction='ignore')
    w.writeheader()
    return f,w

def base_meta(run_id, experiment, config_sha, seed, case, source, target):
    return {
        'run_id':run_id,'timestamp_utc':utc_now(),'experiment':experiment,'config_sha256':config_sha,'seed':seed,
        'case_id':case['case_id'],'workflow_family':case['workflow_family'],'source_runtime':source,'target_runtime':target,
    }
