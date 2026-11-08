# Result Schema

Every correctness row records: run ID, timestamp, experiment, config hash, seed, case ID, workflow family, source runtime, target runtime, condition/method, expected decision, actual decision, safe completion, safe rejection, unsafe violation, and machine-readable reason.

Performance rows additionally record:
`capture_ms, evidence_ms, signing_ms, serialization_ms, transfer_ms, verification_ms, proof_ms, translation_ms, resume_ms, total_ms, raw_checkpoint_bytes, evidence_bytes, certificate_bytes, total_transferred_bytes`.

The semantic performance harness instruments certificate issuance/HMAC generation separately as `signing_ms`, and cryptographic/context verification separately as `verification_ms`. Native framework resume latency remains a separate, explicitly gated experiment.
