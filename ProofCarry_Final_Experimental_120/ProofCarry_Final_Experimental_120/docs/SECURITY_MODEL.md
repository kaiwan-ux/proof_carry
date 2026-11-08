# Security Model

The final experimental authenticator uses HMAC-SHA256 with context-bound certificate fields:

- issuer
- workflow ID
- execution ID
- source runtime
- target runtime
- contract hash
- subject/value
- issue/expiry time
- nonce

It tests certificate mutation, attacker rehashing without the key, replay/context mismatch, wrong workflow, wrong execution, runtime substitution, unauthorized identity binding, expiry, and nonce reuse.

The **hash-only control** deliberately lacks a secret and therefore models integrity without authentication. It can detect accidental non-rehashed mutation but should not be expected to stop an attacker who can modify and recompute an unkeyed digest.

This HMAC experiment does not claim a full production PKI, key-distribution system, revocation service, or distributed replay database. Those remain deployment engineering concerns.
