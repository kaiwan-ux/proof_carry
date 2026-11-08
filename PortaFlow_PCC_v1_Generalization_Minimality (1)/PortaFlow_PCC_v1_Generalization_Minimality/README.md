# PortaFlow PCC v1 — Generalization + Minimality Challenge

This is the **next experiment after PCC v0 ablation**. It is designed to attack the strongest reviewer criticism of the previous result:

> Were the workflows built around the PCC fields, and could a sufficiently strong translator reconstruct most of those fields from ordinary execution history?

This package therefore does **not** repeat the six v0 single-factor workflows. It uses eight hold-out combination workflows and compares explicit PCC semantics against a strong history+static-workflow reconstruction baseline.

## Core research questions

1. Does PCC generalize to unseen workflows that combine multiple continuation hazards?
2. Can rich portable history + static workflow structure reconstruct the same semantics without explicit PCC fields?
3. Which PCC fields remain necessary after reconstruction is allowed?
4. Does PCC mainly improve correctness, or does it improve **safe continuation coverage** by resolving cases that inference must conservatively reject?

## Hold-out workflows

- `branch_effect_approval`
- `loop_effect`
- `parallel_retry_join`
- `retry_effect_uncertain`
- `approval_loop`
- `saga_compensation`
- `nested_parallel_effect`
- `branch_parallel_merge`

Each combines two or more semantic concerns. They are intentionally different from the previous six workflows (`retry`, `approval`, `side_effect`, `branch`, `loop`, `parallel`).

## Representations compared

1. `state_only`
2. `raw_history`
3. `history_inference` — strong reconstruction from non-redacted portable events + static workflow structure; allowed to reject ambiguous migrations safely
4. `full_pcc_v1`
5. `pcc_minus_history`
6. `pcc_minus_frontier`
7. `pcc_minus_obligations`
8. `pcc_minus_receipts`
9. `pcc_minus_contract`

Leave-one-out conditions use the same history reconstruction fallback. This is deliberate: a field only looks necessary if it cannot be reconstructed safely from other portable information.

## Experiment size

- 3 native frameworks
- 6 directed source→target framework pairs
- 8 hold-out workflows
- 9 representations
- **432 configured migration rows**

This is a deterministic designed benchmark, not 432 iid samples. Report exact case counts/proportions; do not attach sampling confidence intervals to duplicated structural cases.

## Strong baseline behavior

`history_inference` may return:

- **safe completion** — it inferred enough semantics,
- **safe rejection** — continuation is ambiguous and it refuses to guess,
- **unsafe violation** — it accepted but got continuation wrong.

A conservative rejection is not counted as successful continuation, but it is separated from unsafe behavior.

## Important anti-cheating rule

PCC payloads cannot contain native framework checkpoints, checkpoint IDs, CrewAI flow IDs, MAF checkpoint blobs, or LangGraph checkpoint contents. Native artifacts are retained only as evidence/provenance outside the capsule.

## Run

Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\run_pcc_v1.ps1
```

or double-click `run_pcc_v1.bat`.

Linux/macOS:

```bash
chmod +x run_pcc_v1.sh
./run_pcc_v1.sh
```

## LLM

No LLM is used in this stage. This is intentional. GPT-OSS-120B is reserved for the later stochastic-agent experiment after the representation survives this generalization/minimality challenge.
