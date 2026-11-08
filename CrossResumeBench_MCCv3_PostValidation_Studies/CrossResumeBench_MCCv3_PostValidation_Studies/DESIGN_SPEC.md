# Design Specification — MCC v3 Post-Validation Studies

## Frozen evidence

The already-passed real holdout is immutable input. Its seven result files are copied under `inputs/passed_holdout/` and protected by SHA-256 checks.

## Study A — paired statistics

Primary unit for inferential analysis: **base workflow case (n=32)**. Row-level migration tests are repeated conditions and must not be treated as 768 independent samples. Primary uncertainty uses base-case block bootstrap and case-level paired Wilcoxon tests. Row-level exact McNemar tests are supplementary.

Primary outcomes: unsafe rate and safe-completion rate. Comparisons: MCC v3 vs frozen MCC v2, history inference, AAIF reference, CapLease reference, AAIF+CapLease reference. Oracle/explicit-minimal remain privileged controls and are descriptive only.

## Study B — ablation

Seven variants: full MCC v3, minus closed-world gate, minus integrity verification, minus identity binding, minus complete snapshots, history-only, and certificates-only. The production mechanism files are never edited. Ablations run in study-layer code.

This is post-validation explanatory analysis on the now-seen holdout semantics, not fresh confirmatory evidence.

## Study C — performance

Mechanism microbenchmark measures build, proof resolution/lowering, total MCC v3 translation, MCC v2 comparison, and payload size. Report median and p95.

Optional native timing uses one canonical case per family, all six directed pairs, and three repeats; it measures source capture, translation, and target continuation separately.
