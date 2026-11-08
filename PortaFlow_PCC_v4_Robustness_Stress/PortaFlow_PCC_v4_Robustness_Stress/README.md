# PortaFlow PCC v4 — Robustness Stress Experiment

This experiment **freezes** the two representations discovered earlier and stress-tests them under evidence corruption and ordering perturbations. It is not another PCC redesign.

## Frozen candidates

- **Hybrid minimal:** semantic history + certified effect receipts + generic reconstruction.
- **Explicit minimal:** control frontier + pending obligations + certified effect receipts + continuation contract.

## Research question

> Do the frozen minimal continuation representations remain safe and useful when portable evidence is noisy, duplicated, reordered, partially missing, or internally contradictory?

## Matrix

8 new robustness workflow families × 5 pre-registered perturbation profiles × 6 directed framework pairs × 5 conditions = **1,200 native runs**.

Profiles:
1. `baseline`
2. `noise_duplicate`
3. `out_of_order`
4. `partial_history_loss`
5. `receipt_conflict`

The experiment measures **safe completion**, **safe rejection**, and **unsafe continuation** separately. A robust portability mechanism is allowed to reject corrupted/insufficient evidence; it must not guess.

## Run

Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\run_robustness.ps1
```

Optional GPT-OSS-120B stage after the deterministic run:

```powershell
Copy-Item .env.example .env
notepad .env
.\run_llm_robustness.ps1
```

The optional model is `openai/gpt-oss-120b` through Groq and is disabled by default.

## What to send back

Upload the generated `PortaFlow_PCC_v4_robustness_results.zip` without editing the files.
