# Security Model

## In scope
- Message/certificate tampering, including attacker-recomputed unkeyed hashes.
- Cross-execution replay.
- Contract substitution.
- Source/target runtime substitution.
- Certificate expiry.
- Nonce reuse.
- Unauthorized semantic identity binding.

## Trust root
The verifier trusts an issuer public key. The benchmark uses a deterministic Ed25519 key solely for reproducibility. Production systems must use protected private keys, issuer rotation/revocation, and durable replay storage.

## Out of scope
- Compromise of the trusted issuer private key.
- Malicious target runtime after verification.
- Side-channel attacks.
- Distributed consensus over multiple issuers.

## Security comparison control
The security study compares ProofCarry against an `unkeyed_hash_control` that checks a recomputable SHA-256 integrity hash but has no issuer authentication, execution/runtime context binding, expiry, nonce replay state, or approved-binding enforcement. This isolates why a bare integrity hash is not equivalent to authenticated evidence.
