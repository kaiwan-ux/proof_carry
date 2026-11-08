from __future__ import annotations

import hashlib
import json
import shutil
import traceback
from pathlib import Path

from .case import case_spec, spec_hash
from .evidence import source_capture_from_native
from .frozen import ROOT, admissibility, build_mcc_v2, reconstruct_mcc_v2
from .ledger import FileLedger
from .models import RunOutcome
from .native import get_runtime

SAFE_LEDGER = {"effect_count": 1, "ack_count": 1, "finish_count": 1}


def _clean(p):
    p = Path(p)
    if p.exists():
        shutil.rmtree(p)
    p.mkdir(parents=True, exist_ok=True)


def _id(*parts):
    return "revb-" + "-".join(str(x) for x in parts)


def _sha(payload):
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def _decision_for_world(world):
    return "skip_effect" if world == "committed" else "execute_effect"


def run(results_dir: Path, runtime_factory=get_runtime):
    cfg = json.loads((ROOT / "config" / "phase1_revisionB.json").read_text(encoding="utf-8"))
    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    for d in [
        results_dir / "artifacts",
        results_dir / "native_sources",
        results_dir / "native_targets",
        results_dir / "work",
    ]:
        d.mkdir(parents=True, exist_ok=True)

    self_rows = []
    source_rows = []
    rows = []
    c = case_spec()
    wh = spec_hash()

    # 1) Native self-resume is a baseline/control, not a prerequisite that must be safe.
    # A technically completed restore that replays an external effect is a scientifically
    # meaningful native-baseline failure, not an adapter technical failure.
    for fw in cfg["frameworks"]:
        rid = _id("self", fw)
        rdir = results_dir / "work" / rid
        _clean(rdir)
        try:
            out = runtime_factory(fw).self_resume_committed(rdir)
            restore_completed = bool(out.get("restore_completed", True))
            safe = bool(out.get("safe", False)) if restore_completed else False
            technical = int(not restore_completed)
            native_unsafe = int(restore_completed and not safe)
            err = ""
            (results_dir / "artifacts" / f"{rid}.json").write_text(
                json.dumps(out, indent=2, default=str), encoding="utf-8"
            )
        except Exception:
            restore_completed = False
            safe = False
            technical = 1
            native_unsafe = 0
            err = traceback.format_exc()
            out = {"error": err}
            (results_dir / "artifacts" / f"{rid}.json").write_text(
                json.dumps(out, indent=2), encoding="utf-8"
            )
        self_rows.append(
            {
                "run_id": rid,
                "framework": fw,
                "case_id": c.case_id,
                "world": "committed",
                "restore_completed": int(restore_completed),
                "self_resume_safe": int(safe),
                "native_unsafe_replay": native_unsafe,
                "technical_failure": technical,
                "error": err,
            }
        )

    # 2) Capture each native source once per hidden world (3*2 = 6).
    source_cache = {}
    source_errors = {}
    for source in cfg["frameworks"]:
        for world in cfg["worlds"]:
            sid = _id("source", source, world)
            sdir = results_dir / "work" / sid
            _clean(sdir)
            try:
                native = runtime_factory(source).capture_effect_pause(sdir, world)
                source_cache[(source, world)] = native
                source_rows.append(
                    {
                        "source_id": sid,
                        "framework": source,
                        "world": world,
                        "capture_success": 1,
                        "technical_failure": 0,
                        "checkpoint_ref": native.checkpoint_ref,
                        "native_kind": native.native_kind,
                        "source_effect_count": native.source_ledger["effect_count"],
                        "pending_work": json.dumps(native.pending_work),
                        "error": "",
                    }
                )
                (results_dir / "native_sources" / f"{sid}.json").write_text(
                    json.dumps(native.to_dict(), indent=2, default=str), encoding="utf-8"
                )
            except Exception:
                err = traceback.format_exc()
                source_errors[(source, world)] = err
                source_rows.append(
                    {
                        "source_id": sid,
                        "framework": source,
                        "world": world,
                        "capture_success": 0,
                        "technical_failure": 1,
                        "checkpoint_ref": "",
                        "native_kind": "",
                        "source_effect_count": "",
                        "pending_work": "",
                        "error": err,
                    }
                )
                (results_dir / "native_sources" / f"{sid}.json").write_text(
                    json.dumps({"error": err}, indent=2), encoding="utf-8"
                )

    # 3) Emit every planned migration row, even when source capture fails.
    for source in cfg["frameworks"]:
        for target in cfg["frameworks"]:
            if target == source:
                continue
            for world in cfg["worlds"]:
                for variant in cfg["evidence_variants"]:
                    for method in cfg["migration_methods"]:
                        rid = _id(source, "to", target, world, variant, method)
                        tdir = results_dir / "work" / rid
                        _clean(tdir)
                        expected_decision = _decision_for_world(world)

                        if (source, world) in source_errors:
                            row = RunOutcome(
                                rid,
                                source,
                                target,
                                c.case_id,
                                world,
                                variant,
                                method,
                                technical_failure=1,
                                failure_types=["SOURCE_CAPTURE_FAILURE"],
                                expected_effect_decision=expected_decision,
                                artifact={"traceback": source_errors[(source, world)]},
                            )
                            rows.append(row.to_dict())
                            (results_dir / "artifacts" / f"{rid}.json").write_text(
                                json.dumps(row.to_dict(), indent=2, default=str), encoding="utf-8"
                            )
                            continue

                        try:
                            native = source_cache[(source, world)]
                            capture = source_capture_from_native(native, variant)
                            FileLedger(tdir / "ledger.json").write(native.source_ledger)

                            if method == "mcc_v2":
                                pkg = build_mcc_v2(capture, target, wh, ROOT / "frozen_v2")
                                ph = _sha(pkg.payload)
                                rc, report = reconstruct_mcc_v2(pkg.payload, c, ROOT / "frozen_v2")
                                accepted, reason = admissibility(rc)

                                if not accepted:
                                    row = RunOutcome(
                                        rid,
                                        source,
                                        target,
                                        c.case_id,
                                        world,
                                        variant,
                                        method,
                                        safe_rejection=1,
                                        reject_reason=reason,
                                        payload_bytes=pkg.byte_size(),
                                        payload_sha256=ph,
                                        expected_effect_decision=expected_decision,
                                        artifact={"payload": pkg.payload, "inference": report},
                                    )
                                else:
                                    fact = rc.effect_facts.get("effect", {}).get("status")
                                    if fact not in {"committed", "not_committed"}:
                                        row = RunOutcome(
                                            rid,
                                            source,
                                            target,
                                            c.case_id,
                                            world,
                                            variant,
                                            method,
                                            unsafe_violation=1,
                                            failure_types=["ACCEPTED_WITHOUT_EFFECT_DECISION"],
                                            payload_bytes=pkg.byte_size(),
                                            payload_sha256=ph,
                                            expected_effect_decision=expected_decision,
                                            artifact={"payload": pkg.payload, "inference": report},
                                        )
                                    else:
                                        out = runtime_factory(target).run_from_effect_decision(fact, tdir)
                                        d = out["ledger"]
                                        actual = out.get("effect_decision", "")
                                        safe = d == SAFE_LEDGER and actual == expected_decision
                                        row = RunOutcome(
                                            rid,
                                            source,
                                            target,
                                            c.case_id,
                                            world,
                                            variant,
                                            method,
                                            safe_completion=int(safe),
                                            unsafe_violation=int(not safe),
                                            failure_types=[] if safe else ["LEDGER_OR_EFFECT_DECISION_MISMATCH"],
                                            payload_bytes=pkg.byte_size(),
                                            payload_sha256=ph,
                                            expected_effect_decision=expected_decision,
                                            actual_effect_decision=actual,
                                            artifact={"payload": pkg.payload, "inference": report, "target": out},
                                        )
                            else:
                                # Privileged controls receive hidden world truth directly.
                                out = runtime_factory(target).run_from_effect_decision(world, tdir)
                                d = out["ledger"]
                                actual = out.get("effect_decision", "")
                                safe = d == SAFE_LEDGER and actual == expected_decision
                                row = RunOutcome(
                                    rid,
                                    source,
                                    target,
                                    c.case_id,
                                    world,
                                    variant,
                                    method,
                                    safe_completion=int(safe),
                                    unsafe_violation=int(not safe),
                                    failure_types=[] if safe else ["CONTROL_FAILED"],
                                    expected_effect_decision=expected_decision,
                                    actual_effect_decision=actual,
                                    artifact={"target": out, "control": "privileged_truth", "world": world},
                                )

                            rows.append(row.to_dict())
                            (results_dir / "artifacts" / f"{rid}.json").write_text(
                                json.dumps(row.to_dict(), indent=2, default=str), encoding="utf-8"
                            )
                            if row.artifact and "target" in row.artifact:
                                (results_dir / "native_targets" / f"{rid}.json").write_text(
                                    json.dumps(row.artifact["target"], indent=2, default=str), encoding="utf-8"
                                )
                        except Exception:
                            row = RunOutcome(
                                rid,
                                source,
                                target,
                                c.case_id,
                                world,
                                variant,
                                method,
                                technical_failure=1,
                                failure_types=["TARGET_OR_TRANSLATION_FAILURE"],
                                expected_effect_decision=expected_decision,
                                artifact={"traceback": traceback.format_exc()},
                            )
                            rows.append(row.to_dict())
                            (results_dir / "artifacts" / f"{rid}.json").write_text(
                                json.dumps(row.to_dict(), indent=2, default=str), encoding="utf-8"
                            )

    import pandas as pd

    pd.DataFrame(self_rows).to_csv(results_dir / "self_resume.csv", index=False)
    pd.DataFrame(source_rows).to_csv(results_dir / "source_capture_results.csv", index=False)
    pd.DataFrame(rows).to_csv(results_dir / "phase1_runs.csv", index=False)
    return self_rows, source_rows, rows
