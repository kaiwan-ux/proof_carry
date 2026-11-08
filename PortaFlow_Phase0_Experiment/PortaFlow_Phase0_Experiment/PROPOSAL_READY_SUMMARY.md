# PortaFlow Phase-0 — Proposal-Ready Experimental Summary

## Problem

Modern agent frameworks can persist/resume their own workflows, but a live workflow state is not standardized across runtimes. A user-visible state dictionary may omit control frontier, retry obligations, pending human interactions, and committed side effects.

## Research question

Can ordinary application state preserve correct continuation when a partially executed workflow moves between heterogeneous agent runtimes?

## Hypothesis for the preliminary experiment

Application state alone will be insufficient for a non-trivial subset of continuation-sensitive workflows. Failures will cluster around control-flow commitments, retries, human approval, and externally committed effects.

## Independent variable

Continuation transfer condition:

- naive state
- state + history
- restart
- full-information oracle upper bound

## Runtime factors

- source framework
- target framework
- workflow pattern
- migration boundary

## Dependent variables

- Safe Continuation Rate
- duplicate effects
- replayed completed steps
- skipped required steps
- lost approvals
- lost retry obligations
- termination correctness

## Controlled variables

- deterministic workflow logic
- identical logical tasks
- identical mock tools
- identical scenario parameters
- no LLM in primary experiment

## Why no LLM in Phase-0?

The first experiment is intended to isolate framework/continuation effects. LLM stochasticity would add noise and make causal interpretation weaker.

## Six representative workflow patterns

Linear, branch, loop, retry, human approval, irreversible side effect.

## Kill criterion

If naïve state transfer reaches ~95% or better safe continuation across representative patterns and additional semantics add negligible benefit, PortaFlow's claimed semantic gap is too weak and the project should pivot.

## Continue criterion

Continue if failures are repeatable, map to multiple missing semantic categories, and an all-information upper bound verifies that correct continuation is possible when the missing information is supplied.

## Next step after Phase-0

Derive PCC fields only from observed failures, then compare the proposed PCC against the same baselines on the exact same benchmark.
