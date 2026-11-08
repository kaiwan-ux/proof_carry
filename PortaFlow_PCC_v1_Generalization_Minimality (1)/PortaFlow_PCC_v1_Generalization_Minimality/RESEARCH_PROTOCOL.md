# Research Protocol — PCC v1 Generalization + Minimality

## Goal

Challenge PCC v0 rather than confirm it. The experiment tests whether explicit continuation semantics generalize to unseen combinations and whether they remain useful when a strong reconstruction algorithm can infer semantics from rich event history and a portable static workflow definition.

## RQ1 — Generalization

Can full PCC safely continue hold-out combination workflows across LangGraph, CrewAI, and Microsoft Agent Framework?

## RQ2 — Reconstruction

How much of PCC can be reconstructed from non-redacted portable history plus static workflow structure?

## RQ3 — Minimality

When one PCC semantic family is removed and a strong reconstruction fallback is allowed, which omissions still reduce safe continuation?

## RQ4 — Coverage versus safety

When history does not determine an external side effect's commit state, can a conservative inference system avoid unsafe replay only by rejecting migration, while PCC receipts permit safe continuation?

## Hypotheses

- **H1:** Full PCC will preserve safe continuation on most hold-out workflows and framework directions.
- **H2:** History+static reconstruction will recover many control, retry, approval, and dependency semantics, reducing the apparent need for explicit fields.
- **H3:** Explicit effect receipts will remain important in at least some cases where observable history cannot establish external commit status.
- **H4:** Some previous PCC components may become redundant under strong reconstruction; if so, PCC should be simplified rather than defended artificially.

## Falsification / pivot rules

### Simplify or pivot PCC if

`history_inference` matches full PCC safe-completion coverage within 5 percentage points **and** rejects <=5% of cases **and** introduces no unsafe violations.

### Reject the current PCC design if

Full PCC achieves <90% safe completion on this controlled hold-out suite without technical failures.

### Minimality warning

If removing every PCC field causes <=1 percentage-point reduction from full PCC after reconstruction fallback, the current representation is over-specified and no minimality claim is supported.

### Strong support for effect receipts

If `pcc_minus_receipts` loses safe completion or causes unsafe effect replay in cases where full PCC succeeds, while history inference must reject those same ambiguous cases, explicit commitment receipts have a stronger empirical justification.

## Metrics

Primary:

- Safe Completion Rate
- Safe Rejection Rate
- Unsafe Violation Rate

Secondary:

- duplicate external effects
- completed-step replay
- continuation trace mismatch
- external-ledger mismatch
- final-outcome mismatch
- inference ambiguity count
- inferred semantic families
- capsule size

## No stochastic statistics yet

These are deterministic designed cases. Use exact counts and proportions. Repeated LLM trials, seeds, confidence intervals, and probabilistic tests belong to the later stochastic-agent stage.
