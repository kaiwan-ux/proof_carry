from __future__ import annotations
import hashlib, json, os, platform, subprocess, sys, uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RUNTIMES = ("langgraph", "crewai", "maf")
RUNTIME_PAIRS = tuple((a,b) for a in RUNTIMES for b in RUNTIMES if a != b)

def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()

def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def new_run_id(prefix="run") -> str:
    return f"{prefix}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"

def git_commit(root: Path) -> str:
    try:
        return subprocess.check_output(["git","rev-parse","HEAD"], cwd=root, stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return "UNAVAILABLE"

def environment_snapshot(root: Path) -> dict:
    pkgs={}
    for name in ["pandas","numpy","scipy","matplotlib","langgraph","crewai","agent_framework"]:
        try:
            mod=__import__(name)
            pkgs[name]=getattr(mod,"__version__","installed-version-unknown")
        except Exception:
            pkgs[name]="NOT_INSTALLED"
    return {
        "timestamp_utc": utc_now(),
        "python": sys.version,
        "platform": platform.platform(),
        "os": os.name,
        "packages": pkgs,
        "git_commit": git_commit(root),
    }
