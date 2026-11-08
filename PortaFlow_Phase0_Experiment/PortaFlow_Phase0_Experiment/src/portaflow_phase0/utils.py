from __future__ import annotations

import hashlib
import json
from pathlib import Path


def load_config(root: Path) -> dict:
    return json.loads((root/"config"/"experiment.json").read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()
