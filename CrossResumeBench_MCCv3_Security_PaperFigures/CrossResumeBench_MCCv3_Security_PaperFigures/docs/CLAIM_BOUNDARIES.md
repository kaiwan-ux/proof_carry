# Claim Boundaries

Safe claims:
- MCC v3 observed 0 unsafe continuations on the sealed 768-condition holdout.
- The closed-world gate is strongly supported by ablation: removing it reintroduced 174 unsafe cases.
- Base-case paired analysis supports significant unsafe-rate reductions versus the tested non-privileged references.
- Current integrity hashes detect non-rehashed evidence mutation.

Do not claim:
- universal zero-failure guarantees;
- superiority to official AAIF/CapLease implementations;
- cryptographic issuer authentication, freshness, anti-replay, or Byzantine security;
- that the security stress study is a new independent native-runtime holdout.
