# Security Threat Model

Current MCC v3 attestations use a trusted-witness integrity hash. The hash covers fact type, subject, value, scope and evidence body.

## In scope
Detection of accidental or unauthenticated mutation after a trusted witness produced the attestation, contract-hash corruption, and conflicting evidence.

## Not provided by the current mechanism
- authenticated issuer identity;
- digital signatures / MACs bound to a secret or public key;
- nonce/freshness enforcement;
- case/workflow-context binding inside the attestation digest;
- replay protection.

The stress test deliberately includes replay and attacker-rehashed forgery to make this boundary explicit.
