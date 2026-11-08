# Research Protocol — PortaFlow PCC v4 Robustness Stress

## Frozen mechanism
No representation fields may be added after observing results.

**Hybrid:** history + effect receipts, with generic normalization/reconstruction/admissibility.

**Explicit:** frontier + obligations + receipts + contract.

## Stress dimensions
- duplicate and irrelevant history events,
- out-of-order portable event delivery (sequence numbers preserved),
- partial loss of a critical reconstructable event,
- contradictory effect receipt vs observable commit acknowledgement.

These perturbations affect **portable evidence**, not native framework internals.

## Primary outcomes
- Safe completion coverage.
- Safe rejection rate.
- Unsafe continuation rate.

Safety is primary. A rejected migration is preferable to replaying an irreversible action.

## Falsification criteria
The frozen mechanism is weakened if:
- hybrid or explicit produces unsafe continuation under any pre-registered corruption profile,
- normalizable noise/order alone substantially reduces safe completion,
- contradictory effect evidence is accepted rather than rejected,
- target-framework results depend strongly on one framework pair.

## Claim boundary
Results support robustness only for this registered workflow/profile/framework matrix. They do not prove universal portability or cryptographic receipt authenticity.
