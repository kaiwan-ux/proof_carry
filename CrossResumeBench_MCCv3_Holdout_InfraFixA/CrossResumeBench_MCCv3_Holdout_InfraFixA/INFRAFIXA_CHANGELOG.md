# InfraFixA Changelog

## Evidence from the interrupted run

The recovered work snapshot showed 8 completed LangGraph probes and 3 completed CrewAI probes, with the CrewAI compensation semantic store already at its correct final state. No MAF probe and no migration table existed. Therefore the interrupted run provides no MCC v3 holdout verdict.

## Infrastructure corrections

- Added subprocess isolation for native gate probes.
- Added subprocess isolation for self-resume and source-capture operations used by the frozen runner.
- Added hard per-call timeout and process-tree termination.
- Added incremental native-gate CSV/JSON persistence after every probe.
- Added lifecycle-return diagnostic separate from semantic correctness.
- Added UTF-8 environment settings for Windows/CrewAI output.
- Added structural result verifier that does not suppress a negative scientific result.
- Added InfraFixA provenance/freeze record.

## Deliberately unchanged

MCC v3 mechanism, holdout suite, evidence, baselines, evaluator, semantics and frozen runner.
