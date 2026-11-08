from __future__ import annotations

import csv
import hashlib
import json
import shutil
import time
import traceback
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from .cases import CASES
from .evidence import generate
from .semantics import expected_final
from .evaluator import evaluate
from .baselines import METHODS, build_and_lower
from .store import SemanticStore
from .infra.isolated_runtime import isolated_runtime_factory

FRAMEWORKS = ["langgraph", "crewai", "maf"]
PAIRS = [(a, b) for a in FRAMEWORKS for b in FRAMEWORKS if a != b]
PROFILE_METHODS = {
    "proofcarry": ["proofcarry"],
    "core": ["proofcarry", "proofcarry_no_auth", "history_only", "always_reject"],
    "full": list(METHODS),
}
DEFAULT_VARIANTS = [
    "enough_evidence",
    "missing_critical_fact",
    "runtime_binding_complete",
    "runtime_binding_missing",
    "irrelevant_noise",
]


def _write_csv(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    keys: list[str] = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({
                k: json.dumps(v, sort_keys=True, default=str) if isinstance(v, (dict, list)) else v
                for k, v in r.items()
            })


def select_cases(preset: str):
    """Select cases without changing the frozen suite.

    all120  : all 15 cases/family (120 total)
    paper104: first 13 cases/family (104 total; matches the expanded-paper scale)
    smoke8  : one representative/family
    smoke24 : three representatives/family
    """
    by_family: dict[str, list] = defaultdict(list)
    for c in CASES:
        by_family[c.family].append(c)
    for fam in by_family:
        by_family[fam] = sorted(by_family[fam], key=lambda x: x.index)
    if preset == "all120":
        out = [c for fam in sorted(by_family) for c in by_family[fam]]
    elif preset == "paper104":
        out = [c for fam in sorted(by_family) for c in by_family[fam][:13]]
    elif preset == "smoke8":
        out = [by_family[fam][0] for fam in sorted(by_family)]
    elif preset == "smoke24":
        out = [c for fam in sorted(by_family) for c in by_family[fam][:3]]
    else:
        raise ValueError(f"unknown case preset: {preset}")
    return out


def expected_counts(cases, variants, methods):
    n = len(cases)
    return {
        "cases": n,
        "families": len({c.family for c in cases}),
        "frameworks": len(FRAMEWORKS),
        "pairs": len(PAIRS),
        "variants": len(variants),
        "methods": len(methods),
        "family_gate_rows": len({c.family for c in cases}) * len(FRAMEWORKS),
        "self_resume_rows": n * len(FRAMEWORKS),
        "source_capture_rows": n * len(FRAMEWORKS),
        "migration_rows": n * len(PAIRS) * len(variants) * len(methods),
    }


def capability_doctor(results: Path, runtime_factory=isolated_runtime_factory):
    rows = []
    for fw in FRAMEWORKS:
        t0 = time.perf_counter()
        try:
            d = runtime_factory(fw).capability_probe()
            rows.append({
                "framework": fw,
                "installed": int(bool(d.get("installed"))),
                "ready": int(bool(d.get("ready"))),
                "version": d.get("version", "unknown"),
                "pause_kind": d.get("pause_kind", ""),
                "semantic_namespace": d.get("semantic_namespace", ""),
                "duration_ms": (time.perf_counter() - t0) * 1000,
                "error": "",
                "details": d,
            })
        except Exception:
            rows.append({
                "framework": fw,
                "installed": 0,
                "ready": 0,
                "version": "unavailable",
                "pause_kind": "",
                "semantic_namespace": "",
                "duration_ms": (time.perf_counter() - t0) * 1000,
                "error": traceback.format_exc(),
                "details": {},
            })
    _write_csv(results / "native_environment.csv", rows)
    (results / "native_environment.json").write_text(
        json.dumps({r["framework"]: r for r in rows}, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )
    return rows


def native_family_gate(cases, results: Path, runtime_factory=isolated_runtime_factory):
    rows: list[dict] = []
    by_family = defaultdict(list)
    for c in cases:
        by_family[c.family].append(c)
    for fw in FRAMEWORKS:
        for fam in sorted(by_family):
            case = sorted(by_family[fam], key=lambda c: c.index)[0]
            rd = results / "native_work" / f"gate-{fw}-{case.case_id}"
            shutil.rmtree(rd, ignore_errors=True)
            rd.mkdir(parents=True, exist_ok=True)
            t0 = time.perf_counter()
            try:
                out = runtime_factory(fw).self_resume_case(case, rd)
                good = bool(out.get("restore_completed") and out.get("safe"))
                err = ""
                lifecycle = bool(out.get("lifecycle_returned", True))
                status = out.get("isolated_status", "ok")
            except Exception:
                good = False
                err = traceback.format_exc()
                lifecycle = False
                status = "technical_failure"
            rows.append({
                "framework": fw,
                "family": fam,
                "case_id": case.case_id,
                "pass": int(good),
                "lifecycle_returned": int(lifecycle),
                "status": status,
                "duration_ms": (time.perf_counter() - t0) * 1000,
                "error": err,
            })
    _write_csv(results / "native_family_gate.csv", rows)
    return rows


def _gate_map(gate_rows):
    return {(r["framework"], r["family"]): bool(int(r["pass"])) for r in gate_rows}


def _technical_row(rid, case, source, target, variant, method, reason, error=""):
    return {
        "run_id": rid,
        "study": "native_full",
        "source": source,
        "target": target,
        "case_id": case.case_id,
        "family": case.family,
        "condition": variant,
        "method": method,
        "safe_completion": 0,
        "safe_rejection": 0,
        "unsafe_violation": 0,
        "technical_failure": 1,
        "reject_reason": reason,
        "failure_types": [],
        "payload_bytes": 0,
        "proof_latency_ms": 0.0,
        "target_runtime_latency_ms": 0.0,
        "total_latency_ms": 0.0,
        "error": error,
    }


def run_native_full(
    results: Path,
    *,
    case_preset: str = "all120",
    profile: str = "proofcarry",
    variants: Iterable[str] = DEFAULT_VARIANTS,
    runtime_factory=isolated_runtime_factory,
):
    results = Path(results)
    results.mkdir(parents=True, exist_ok=True)
    (results / "native_work").mkdir(parents=True, exist_ok=True)

    cases = select_cases(case_preset)
    methods = PROFILE_METHODS[profile]
    variants = list(variants)
    counts = expected_counts(cases, variants, methods)
    (results / "NATIVE_EXPECTED_COUNTS.json").write_text(json.dumps(counts, indent=2), encoding="utf-8")

    env_rows = capability_doctor(results, runtime_factory)
    env_ready = {r["framework"]: bool(int(r["ready"])) for r in env_rows}
    env_version = {r["framework"]: r.get("version", "unknown") for r in env_rows}

    gate_rows = native_family_gate(cases, results, runtime_factory)
    gate = _gate_map(gate_rows)

    self_rows: list[dict] = []
    source_rows: list[dict] = []
    cache = {}
    source_errors = {}

    # Full self-resume and source-capture controls. Family-gate failures are not
    # repeatedly executed; they are recorded explicitly as technical blockers.
    for fw in FRAMEWORKS:
        for case in cases:
            family_ready = env_ready.get(fw, False) and gate.get((fw, case.family), False)

            if not family_ready:
                reason = "ENVIRONMENT_OR_FAMILY_GATE_FAILED"
                self_rows.append({
                    "framework": fw, "framework_version": env_version.get(fw),
                    "case_id": case.case_id, "family": case.family,
                    "safe": 0, "technical_failure": 1,
                    "lifecycle_returned": 0, "duration_ms": 0.0,
                    "error": reason,
                })
                source_rows.append({
                    "framework": fw, "framework_version": env_version.get(fw),
                    "case_id": case.case_id, "family": case.family,
                    "capture_success": 0, "technical_failure": 1,
                    "native_checkpoint_bytes": 0, "native_pause_metadata_bytes": 0,
                    "checkpoint_measurement_kind": "not_run_gate_failed",
                    "duration_ms": 0.0, "error": reason,
                })
                source_errors[(fw, case.case_id)] = reason
                continue

            rd = results / "native_work" / f"self-{fw}-{case.case_id}"
            shutil.rmtree(rd, ignore_errors=True)
            rd.mkdir(parents=True, exist_ok=True)
            t0 = time.perf_counter()
            try:
                out = runtime_factory(fw).self_resume_case(case, rd)
                tech = 0
                safe = int(bool(out.get("restore_completed") and out.get("safe")))
                lifecycle = int(bool(out.get("lifecycle_returned", True)))
                status = out.get("isolated_status", "ok")
                err = ""
            except Exception:
                tech = 1; safe = 0; lifecycle = 0; status = "technical_failure"; err = traceback.format_exc()
            self_rows.append({
                "framework": fw, "framework_version": env_version.get(fw),
                "case_id": case.case_id, "family": case.family,
                "safe": safe, "technical_failure": tech,
                "lifecycle_returned": lifecycle,
                "status": status,
                "duration_ms": (time.perf_counter() - t0) * 1000,
                "error": err,
            })

            rd = results / "native_work" / f"capture-{fw}-{case.case_id}"
            shutil.rmtree(rd, ignore_errors=True)
            rd.mkdir(parents=True, exist_ok=True)
            t0 = time.perf_counter()
            try:
                n = runtime_factory(fw).capture_case_pause(case, rd)
                cache[(fw, case.case_id)] = n
                tech = 0; err = ""
                cpdir = rd / "checkpoints"
                checkpoint_bytes = sum(p.stat().st_size for p in cpdir.rglob("*") if p.is_file()) if cpdir.exists() else 0
                pause_metadata_bytes = len(json.dumps(n.to_dict(), sort_keys=True, separators=(",", ":"), default=str).encode())
                measurement_kind = "checkpoint_files" if checkpoint_bytes > 0 else "in_memory_or_framework_managed"
            except Exception:
                tech = 1; err = traceback.format_exc(); source_errors[(fw, case.case_id)] = err
                checkpoint_bytes = 0; pause_metadata_bytes = 0; measurement_kind = "technical_failure"
            source_rows.append({
                "framework": fw, "framework_version": env_version.get(fw),
                "case_id": case.case_id, "family": case.family,
                "capture_success": int(not tech), "technical_failure": tech,
                "native_checkpoint_bytes": checkpoint_bytes,
                "native_pause_metadata_bytes": pause_metadata_bytes,
                "checkpoint_measurement_kind": measurement_kind,
                "duration_ms": (time.perf_counter() - t0) * 1000,
                "error": err,
            })

    _write_csv(results / "native_self_resume.csv", self_rows)
    _write_csv(results / "native_source_captures.csv", source_rows)

    rows: list[dict] = []
    for case in cases:
        exp = expected_final(case)
        for source, target in PAIRS:
            for variant in variants:
                for method in methods:
                    rid = f"native|{case.case_id}|{source}->{target}|{variant}|{method}"
                    total_t0 = time.perf_counter()
                    if not gate.get((source, case.family), False):
                        rows.append(_technical_row(rid, case, source, target, variant, method, "SOURCE_FAMILY_GATE_FAILED")); continue
                    if not gate.get((target, case.family), False):
                        rows.append(_technical_row(rid, case, source, target, variant, method, "TARGET_FAMILY_GATE_FAILED")); continue
                    if (source, case.case_id) in source_errors or (source, case.case_id) not in cache:
                        rows.append(_technical_row(rid, case, source, target, variant, method, "SOURCE_CAPTURE_FAILED", source_errors.get((source, case.case_id), "missing capture"))); continue

                    rd = results / "native_work" / hashlib.sha256(rid.encode()).hexdigest()
                    shutil.rmtree(rd, ignore_errors=True)
                    rd.mkdir(parents=True, exist_ok=True)
                    try:
                        cap = generate(case, cache[(source, case.case_id)], source, target, variant)
                        proof_t0 = time.perf_counter()
                        payload, plan, reject, report = build_and_lower(method, cap, case, target)
                        proof_ms = (time.perf_counter() - proof_t0) * 1000
                        pb = len(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode())

                        common = {
                            "run_id": rid, "study": "native_full",
                            "source": source, "target": target,
                            "source_version": env_version.get(source), "target_version": env_version.get(target),
                            "case_id": case.case_id, "family": case.family,
                            "condition": variant, "method": method,
                            "source_checkpoint_ref": cache[(source, case.case_id)].checkpoint_ref,
                            "source_native_kind": cache[(source, case.case_id)].native_kind,
                            "payload_bytes": pb, "proof_latency_ms": proof_ms,
                            "gate_source_pass": 1, "gate_target_pass": 1,
                        }
                        if plan is None:
                            rows.append({**common,
                                "safe_completion": 0, "safe_rejection": 1,
                                "unsafe_violation": 0, "technical_failure": 0,
                                "reject_reason": reject, "failure_types": [],
                                "target_runtime_executed": 0,
                                "target_runtime_latency_ms": 0.0,
                                "total_latency_ms": (time.perf_counter() - total_t0) * 1000,
                                "error": "",
                            })
                            continue

                        # Seed the target with the source semantic store and then require
                        # the target framework to execute the lowered continuation plan.
                        SemanticStore(rd / "semantic_store.json").write(cache[(source, case.case_id)].source_store)
                        target_t0 = time.perf_counter()
                        out = runtime_factory(target).run_plan(case, plan, rd)
                        target_ms = (time.perf_counter() - target_t0) * 1000
                        safe, fail = evaluate(exp, out["store"])
                        rows.append({**common,
                            "safe_completion": int(safe), "safe_rejection": 0,
                            "unsafe_violation": int(not safe), "technical_failure": 0,
                            "reject_reason": "", "failure_types": fail,
                            "target_runtime_executed": 1,
                            "target_native_kind": out.get("native_kind", ""),
                            "target_runtime_latency_ms": target_ms,
                            "total_latency_ms": (time.perf_counter() - total_t0) * 1000,
                            "error": "",
                        })
                    except Exception:
                        r = _technical_row(rid, case, source, target, variant, method, "NATIVE_EXECUTION_EXCEPTION", traceback.format_exc())
                        r["source_version"] = env_version.get(source)
                        r["target_version"] = env_version.get(target)
                        r["total_latency_ms"] = (time.perf_counter() - total_t0) * 1000
                        rows.append(r)

    _write_csv(results / "native_runs.csv", rows)
    return {
        "expected": counts,
        "actual": {
            "family_gate_rows": len(gate_rows),
            "self_resume_rows": len(self_rows),
            "source_capture_rows": len(source_rows),
            "migration_rows": len(rows),
        },
        "case_preset": case_preset,
        "profile": profile,
        "variants": variants,
        "methods": methods,
    }
