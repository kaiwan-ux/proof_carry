# Strong history-inference baseline

The baseline receives:

1. the non-redacted portable event stream produced by the benchmark instrumentation, and
2. the static workflow structure.

It may infer:

- completed steps from step-completion events,
- retry progress from failed/succeeded attempt events,
- branch choices from decision events,
- loop counters from iteration events,
- unresolved approvals from request-without-response pairs,
- dependency/join structure from the static workflow model,
- effect receipts only when an explicit commit acknowledgement exists.

If a tool call may have committed externally but the event stream only shows a timeout/unknown commit status, the baseline is allowed to reject migration. It is not forced to replay the operation.

This is intentionally stronger than the v0 history baseline.
