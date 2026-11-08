from __future__ import annotations

import json
import shutil
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "frozen_v2" / "src")]

from crossresumebench_v3_revc.ledger import FileLedger
from crossresumebench_v3_revc.native.maf_runtime import MAFRuntime

SAFE = {"effect_count": 1, "ack_count": 1, "finish_count": 1}
OUT = ROOT / "results" / "MAF_REVISIONC_PROBE.json"
WORK = ROOT / "results" / "maf_probe_work"


def clean(path: Path):
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def main() -> int:
    clean(WORK)
    rt = MAFRuntime()
    result = {
        "probe": "CrossResumeBench_v3_Phase1_RevisionC_MAF_native_gate",
        "purpose": "Validate MAF explicit handler types, real checkpoint capture, native restore, and target effect decisions before the 72-row grid.",
        "checks": {},
        "pass": False,
    }

    try:
        result["capability"] = rt.capability_probe()
        result["checks"]["capability_ready"] = bool(result["capability"].get("ready"))
    except Exception:
        result["capability_error"] = traceback.format_exc()
        result["checks"]["capability_ready"] = False

    # 1) Native committed self-resume.
    try:
        sr = rt.self_resume_committed(WORK / "self_resume")
        result["self_resume"] = sr
        result["checks"]["self_resume_restores"] = bool(sr.get("restore_completed"))
        result["checks"]["self_resume_safe"] = bool(sr.get("safe")) and sr.get("ledger") == SAFE
    except Exception:
        result["self_resume_error"] = traceback.format_exc()
        result["checks"]["self_resume_restores"] = False
        result["checks"]["self_resume_safe"] = False

    # 2) Both hidden worlds must stop before ack, with source ledger truth preserved.
    captures = {}
    for world, expected_effect in [("committed", 1), ("not_committed", 0)]:
        try:
            pause = rt.capture_effect_pause(WORK / f"capture_{world}", world)
            captures[world] = pause.to_dict()
            expected = {"effect_count": expected_effect, "ack_count": 0, "finish_count": 0}
            result["checks"][f"capture_{world}"] = pause.source_ledger == expected and pause.pending_work == ["ack"]
        except Exception:
            captures[world] = {"error": traceback.format_exc()}
            result["checks"][f"capture_{world}"] = False
    result["captures"] = captures

    # 3) Target committed decision must skip; not_committed must execute exactly once.
    target_results = {}
    for status, starting_effect, expected_decision in [
        ("committed", 1, "skip_effect"),
        ("not_committed", 0, "execute_effect"),
    ]:
        tdir = WORK / f"target_{status}"
        clean(tdir)
        FileLedger(tdir / "ledger.json").write({"effect_count": starting_effect, "ack_count": 0, "finish_count": 0})
        try:
            out = rt.run_from_effect_decision(status, tdir)
            target_results[status] = out
            result["checks"][f"target_{status}"] = out.get("ledger") == SAFE and out.get("effect_decision") == expected_decision
        except Exception:
            target_results[status] = {"error": traceback.format_exc()}
            result["checks"][f"target_{status}"] = False
    result["targets"] = target_results

    result["pass"] = bool(result["checks"]) and all(result["checks"].values())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    if not result["pass"]:
        print(f"MAF REVISION C PROBE FAIL. Diagnostic written to {OUT}", file=sys.stderr)
        return 2
    print("MAF REVISION C PROBE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
