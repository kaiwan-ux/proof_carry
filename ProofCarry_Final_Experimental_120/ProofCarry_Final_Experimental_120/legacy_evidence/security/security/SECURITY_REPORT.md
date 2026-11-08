# MCC v3 Security Stress Report

- Rows: 768
- In-threat-model integrity gate: **PASS**
- Trust boundary exposed by out-of-model attacks: **True**

## Outcomes
- safe_completion: 96
- safe_rejection: 480
- unsafe: 192

## By variant
- valid_control: {'safe_completion': 96}
- value_tamper_no_rehash: {'safe_rejection': 96}
- subject_tamper_no_rehash: {'safe_rejection': 96}
- evidence_tamper_no_rehash: {'safe_rejection': 96}
- contract_hash_tamper: {'safe_rejection': 96}
- conflicting_valid_certificates: {'safe_rejection': 96}
- cross_context_replay: {'unsafe': 96}
- forged_rehash_wrong_value: {'unsafe': 96}

## Interpretation
Hash integrity detects non-rehashed mutation, but does not authenticate issuer authority or bind certificates to a unique case/context. Out-of-model forged/replayed valid hashes are expected to expose this boundary.
