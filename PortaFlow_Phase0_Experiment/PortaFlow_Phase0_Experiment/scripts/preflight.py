from __future__ import annotations

import importlib
import json
import platform
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PACKAGES = [
    ("langgraph", "langgraph"),
    ("crewai", "crewai"),
    ("agent-framework", "agent_framework"),
    ("pandas", "pandas"),
    ("matplotlib", "matplotlib"),
]


def main() -> int:
    report = {
        "python": sys.version,
        "platform": platform.platform(),
        "packages": {},
    }
    print("PortaFlow Phase-0 preflight")
    print("Python:", sys.version.split()[0])
    if sys.version_info < (3, 11):
        print("ERROR: Python 3.11+ is required.")
        return 2
    for dist, module in PACKAGES:
        item = {"importable": False, "version": None, "error": None}
        try:
            importlib.import_module(module)
            item["importable"] = True
        except Exception as e:
            item["error"] = f"{type(e).__name__}: {e}"
        try:
            item["version"] = version(dist)
        except PackageNotFoundError:
            pass
        report["packages"][dist] = item
        print(f"{dist:18} importable={item['importable']} version={item['version']}")
    (ROOT/"results"/"PREFLIGHT.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    # Core harness may run even when one native framework is unavailable.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
