# Design Specification

## Central question
Can authenticated proof-carrying continuation preserve useful cross-runtime completion while rejecting migrations whose continuation-critical state, identity mapping, or certificate context cannot be verified?

## Independent experimental unit
A **base case** is the primary independent unit. There are 104 cases, not 31,200 independent observations. Framework directions, evidence variants, methods, attacks, and repeats are repeated measurements.

## Families
Effect commitment, retry, approval, parallel join, loop, compensation, callback, and composite.

## Runtime-specific semantic translation
Each canonical continuation subject has distinct runtime-native aliases. Source evidence is expressed using the source alias; the target contract requires the target alias. Signed identity-binding certificates map both aliases to the canonical semantic subject. Missing or unauthorized bindings must reject.

## Certificate context
Ed25519 certificates bind: issuer ID, execution ID, case ID, workflow-spec hash, contract hash, source runtime, target runtime, issue/expiry times, nonce, fact type, subject, value, and evidence metadata.

## Main studies
1. Semantic scale and baseline comparison.
2. Native cross-runtime confirmation.
3. Cryptographic/context-binding security.
4. Component ablation.
5. End-to-end latency and evidence efficiency.

## No oracle leakage
The ProofCarry mechanism imports neither case truth nor oracle plans. Truth is used only by the benchmark evidence issuer/evaluator; the target planner consumes only proven facts and public workflow semantics.
