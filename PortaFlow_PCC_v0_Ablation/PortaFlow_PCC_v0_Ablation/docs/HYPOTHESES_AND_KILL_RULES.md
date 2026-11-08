# Hypotheses and Kill Rules

## H1 — mechanism value

`SCR(full_pcc_v0) > SCR(state_history)`.

If false or the gain is negligible across meaningful workflows, redesign or reject PCC v0.

## H2 — effect receipt value

Adding effect receipts should reduce `DUPLICATE_EXTERNAL_EFFECT` on the committed-side-effect workflow.

If effect receipts do not change this failure mode, the current receipt mechanism is wrong or redundant.

## H3 — semantic component specificity

- control frontier should matter for branch/loop continuation;
- pending obligations should matter for live approval continuation;
- dependency contract should matter for partial parallel completion.

A component that never changes an outcome in its intended class should not be claimed as required.

## Research discipline

Unexpected results are useful. Do not modify evaluator rules after seeing results merely to make PCC win. If a framework exposes enough portable information through simpler means, treat that as evidence against unnecessary PCC complexity.
