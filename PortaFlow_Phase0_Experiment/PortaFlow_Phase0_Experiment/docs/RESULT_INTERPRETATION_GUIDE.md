# Result Interpretation Guide

## Do not report controlled-model numbers as native framework results

`raw_runs.csv` is a controlled capsule-sufficiency matrix. It validates the measurement logic and generates the planned failure taxonomy. The column `evidence_tier=controlled_model` makes this explicit.

Native runtime evidence is in:

- `results/native_probe_summary.csv`
- `results/native/langgraph.json`
- `results/native/crewai.json`
- `results/native/maf.json`

## A strong preliminary result

A strong result has all of the following:

1. same-runtime/native probes technically succeed,
2. the runtimes expose meaningfully different resume/checkpoint representations,
3. ordinary state/history loses at least two semantic categories in realistic continuation cases,
4. failures are contract violations rather than only different textual outputs,
5. the oracle/full-information check demonstrates that the target continuation is expressible,
6. technical failures are low enough that conclusions are not dominated by broken installations.

## A weak result

The direction is weak if ordinary state/history is sufficient for almost all realistic cases, failures are only artificial restart/replay examples, or the target frameworks cannot express the workflows at all.

## What to send for analysis

Send the entire `results` folder, not screenshots or selected CSV rows.
