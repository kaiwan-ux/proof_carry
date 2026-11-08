# Design Specification

## Research question
Can closed-world proof obligations eliminate MCC v2's unsafe "missing evidence => no obligation" behavior while preserving useful cross-runtime continuation coverage on a fresh unseen holdout?

## New mechanism
A target workflow publishes a continuation contract containing only the fact keys needed to choose a safe continuation. The source payload carries evidence, not truth. MCC v3 resolves contract facts from history, verified attestations, identity bindings and complete-domain snapshots. Missing or conflicting required facts are rejected.

## Fresh holdout
32 cases: 4 each across effect, retry, approval, parallel, loop, compensation, callback, plus 4 composites. Each case has four preregistered evidence variants. The holdout was generated after the mechanism freeze.

## Claims if successful
A successful holdout supports safety of this proof-obligation mechanism for the tested continuation contracts and runtimes. It does not prove arbitrary-agent migration or adversarial certificate security. Attestations use a trusted-witness/hash assumption, not digital signatures.
