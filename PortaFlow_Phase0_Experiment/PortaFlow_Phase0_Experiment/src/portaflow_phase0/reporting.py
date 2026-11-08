from __future__ import annotations

import json
import math
import os
import platform
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1 + z*z/n
    center = (p + z*z/(2*n))/den
    margin = z * math.sqrt((p*(1-p)/n) + z*z/(4*n*n))/den
    return max(0, center-margin), min(1, center+margin)


def analyze(root: Path) -> None:
    r = root / "results"
    raw = pd.read_csv(r / "raw_runs.csv")
    semantic = raw[raw["technical_failure"] == 0].copy()

    summary = semantic.groupby(["condition"], dropna=False).agg(
        runs=("run_id", "count"),
        safe=("safe_continuation", "sum"),
        scr=("safe_continuation", "mean"),
        duplicate_effects=("duplicate_effects", "sum"),
        replayed_steps=("replayed_steps", "sum"),
        skipped_required_steps=("skipped_required_steps", "sum"),
    ).reset_index()
    summary["wilson_low"] = [wilson(int(k), int(n))[0] for k,n in zip(summary.safe, summary.runs)]
    summary["wilson_high"] = [wilson(int(k), int(n))[1] for k,n in zip(summary.safe, summary.runs)]
    summary.to_csv(r / "execution_summary.csv", index=False)

    semantic[semantic.safe_continuation == 0].to_csv(r / "failure_cases.csv", index=False)

    pair = semantic.groupby(["source_framework","target_framework","condition"]).safe_continuation.mean().reset_index(name="scr")
    pair.to_csv(r / "framework_pair_summary.csv", index=False)

    wf = semantic.groupby(["workflow","condition"]).agg(runs=("run_id","count"), scr=("safe_continuation","mean")).reset_index()
    wf.to_csv(r / "workflow_summary.csv", index=False)

    c = Counter()
    for x in semantic.failure_types.fillna(""):
        for f in str(x).split(";"):
            if f:
                c[f] += 1
    pd.DataFrame([{"failure_type":k,"count":v} for k,v in c.most_common()]).to_csv(r / "failure_taxonomy.csv", index=False)

    _graphs(r, semantic, summary, wf, pair, c)
    _analysis_md(r, raw, semantic, summary, c)
    _execution_report(r, raw, summary)
    _environment(r)


def _graphs(r: Path, semantic: pd.DataFrame, summary: pd.DataFrame, wf: pd.DataFrame, pair: pd.DataFrame, c: Counter) -> None:
    g = r / "graphs"; g.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(8,5))
    ax.bar(summary.condition, summary.scr)
    ax.set_ylim(0,1); ax.set_ylabel("Safe Continuation Rate"); ax.set_title("Safe continuation by transfer condition")
    ax.tick_params(axis="x", rotation=20); fig.tight_layout(); fig.savefig(g/"safe_continuation_rate.png", dpi=180); plt.close(fig)

    pivot = wf.pivot(index="workflow", columns="condition", values="scr").fillna(0)
    fig, ax = plt.subplots(figsize=(9,5)); pivot.plot(kind="bar", ax=ax); ax.set_ylim(0,1); ax.set_ylabel("SCR"); ax.set_title("Safe continuation by workflow")
    fig.tight_layout(); fig.savefig(g/"failures_by_workflow.png", dpi=180); plt.close(fig)

    if c:
        labels=[x[0] for x in c.most_common()]; vals=[x[1] for x in c.most_common()]
        fig, ax = plt.subplots(figsize=(9,5)); ax.bar(labels, vals); ax.set_ylabel("Failure count"); ax.set_title("Failure type distribution"); ax.tick_params(axis="x", rotation=35)
        fig.tight_layout(); fig.savefig(g/"failure_type_distribution.png", dpi=180); plt.close(fig)

    # Pair matrix for naive_state; controlled harness only.
    p = pair[pair.condition=="naive_state"].pivot(index="source_framework", columns="target_framework", values="scr").fillna(0)
    fig, ax = plt.subplots(figsize=(6,5)); im=ax.imshow(p.values, vmin=0, vmax=1); ax.set_xticks(range(len(p.columns)),p.columns); ax.set_yticks(range(len(p.index)),p.index)
    for i in range(len(p.index)):
        for j in range(len(p.columns)):
            ax.text(j,i,f"{p.iloc[i,j]:.2f}",ha="center",va="center")
    ax.set_title("Naive-state SCR matrix (controlled model)"); fig.colorbar(im, ax=ax); fig.tight_layout(); fig.savefig(g/"framework_pair_matrix.png", dpi=180); plt.close(fig)

    inv_names = ["approval_preserved","retry_preserved","correct_termination"]
    inv = semantic.groupby("condition")[inv_names].mean()
    fig, ax = plt.subplots(figsize=(8,5)); inv.plot(kind="bar", ax=ax); ax.set_ylim(0,1); ax.set_ylabel("Pass rate"); ax.set_title("Selected invariant pass rates")
    fig.tight_layout(); fig.savefig(g/"invariant_pass_rates.png", dpi=180); plt.close(fig)


def _analysis_md(r: Path, raw: pd.DataFrame, semantic: pd.DataFrame, summary: pd.DataFrame, c: Counter) -> None:
    lines = [
        "# Phase-0 Automated Analysis Summary", "",
        "> IMPORTANT: the systematic matrix in `raw_runs.csv` is marked `controlled_model`. It tests capsule sufficiency and must not be described as native framework evidence. Native framework probes are reported separately.", "",
        f"Total controlled runs: **{len(raw)}**", f"Technical failures: **{int(raw.technical_failure.sum())}**", "",
        "## Safe Continuation Rate by condition", "",
        "| Condition | Runs | Safe | SCR | 95% Wilson CI |", "|---|---:|---:|---:|---:|",
    ]
    for _,x in summary.iterrows():
        lines.append(f"| {x.condition} | {int(x.runs)} | {int(x.safe)} | {x.scr:.3f} | [{x.wilson_low:.3f}, {x.wilson_high:.3f}] |")
    lines += ["", "## Failure taxonomy", ""]
    if c:
        for k,v in c.most_common(): lines.append(f"- **{k}**: {v}")
    else:
        lines.append("- No semantic failures recorded.")
    lines += ["", "## Decision rule", "",
              "Do not make the final GO/NO-GO decision from the controlled model alone. Use it to validate the measurement pipeline, then inspect `native_probe_summary.csv` and the native JSON artifacts. If native evidence plus controlled continuation tests show repeated losses around multiple semantic categories, proceed to PCC v0. If ordinary state is sufficient in native cross-runtime implementations, pivot."]
    (r/"ANALYSIS_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")


def _execution_report(r: Path, raw: pd.DataFrame, summary: pd.DataFrame) -> None:
    txt = ["PORTAFLOW PHASE-0 EXECUTION REPORT", "="*38, f"runs={len(raw)}", f"technical_failures={int(raw.technical_failure.sum())}"]
    for _,x in summary.iterrows(): txt.append(f"{x.condition}: SCR={x.scr:.4f} ({int(x.safe)}/{int(x.runs)})")
    (r/"EXECUTION_REPORT.txt").write_text("\n".join(txt)+"\n", encoding="utf-8")


def _environment(r: Path) -> None:
    try:
        freeze = subprocess.check_output([sys.executable,"-m","pip","freeze"], text=True, stderr=subprocess.STDOUT, timeout=30).splitlines()
    except Exception as e:
        freeze = [f"pip freeze unavailable: {e}"]
    data = {"python":sys.version,"platform":platform.platform(),"executable":sys.executable,"packages":freeze}
    (r/"ENVIRONMENT.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
