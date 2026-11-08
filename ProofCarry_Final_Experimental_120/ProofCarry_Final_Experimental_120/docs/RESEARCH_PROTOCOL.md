# Final Research Protocol

## Q1 — Is ProofCarry safer than practical baselines?
Use the immutable 32-case sealed holdout plus the expanded benchmark. Primary outcomes: unsafe continuation, safe completion, safe rejection. Primary statistical unit is the **base case**, not the repeated runtime-pair row.

## Q2 — Does the behavior persist over broader semantic cases?
Run Expanded120: 8 families x 15 distinct cases. Systematic evidence variants are orthogonal stress conditions, not counted as new base cases.

## Q3 — Why is it safe?
Run component ablations. The primary mechanistic contrast is full ProofCarry vs removal of the closed-world gate. Authentication, identity binding, complete snapshots, dependency reasoning, and certificate verification are also ablated.

## Q4 — Can evidence manipulation bypass admission?
Run nine attacks against authenticated ProofCarry and an unkeyed hash-only control. Report attack-specific rejection/unsafe rates. HMAC is a reproducible authenticated-control mechanism, not a claim of production PKI completeness.

## Q5 — Does cross-runtime semantic identity matter?
For every directed pair among LangGraph, CrewAI, and Microsoft Agent Framework, test correct, missing, wrong, and ambiguous identity mappings using runtime-specific task/checkpoint identifiers.

## Q6 — What does it cost?
Measure semantic end-to-end pipeline latency and payload. Report mean, std, min, median, p95, p99, max. Native framework end-to-end latency is a separate experiment and must not be inferred from semantic timing.

## Statistical protocol
- Aggregate repeated runtime-pair/evidence observations within each base case.
- Case-block bootstrap 95% confidence intervals.
- Paired Wilcoxon signed-rank tests on case-level rates.
- Holm correction across method comparisons.
- Report absolute percentage-point differences and rank-biserial effect size.
- Do not call significance unless the generated statistical file supports it.
