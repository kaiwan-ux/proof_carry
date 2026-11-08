from __future__ import annotations
import hashlib, hmac, json
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Set, Tuple
from .utils import canonical_json
from .types import RuntimeContext, RejectReason

DEFAULT_TEST_KEY = b"PROOFCARRY_TEST_ONLY_KEY_CHANGE_FOR_DEPLOYMENT"
ALLOWED_ISSUERS = {"trusted-runtime-witness", "trusted-effect-service", "trusted-orchestrator"}

def _payload(cert: Dict[str, Any]) -> Dict[str, Any]:
    return {k:v for k,v in cert.items() if k not in {"mac","digest"}}

def digest_payload(cert: Dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(_payload(cert)).encode()).hexdigest()

def mac_payload(cert: Dict[str, Any], key: bytes) -> str:
    return hmac.new(key, canonical_json(_payload(cert)).encode(), hashlib.sha256).hexdigest()

def issue_certificate(*, subject: str, value: Any, context: RuntimeContext,
                      issuer: str="trusted-runtime-witness", nonce: str,
                      ttl_seconds: int=3600, key: bytes=DEFAULT_TEST_KEY,
                      kind: str="fact") -> Dict[str, Any]:
    now=datetime.now(timezone.utc)
    cert={
        "cert_version":"proofcarry-cert-v1",
        "kind":kind,
        "issuer":issuer,
        "subject":subject,
        "value":value,
        "workflow_id":context.workflow_id,
        "execution_id":context.execution_id,
        "source_runtime":context.source_runtime,
        "target_runtime":context.target_runtime,
        "contract_hash":context.contract_hash,
        "issued_at":now.isoformat(),
        "expires_at":(now+timedelta(seconds=ttl_seconds)).isoformat(),
        "nonce":nonce,
    }
    cert["digest"]=digest_payload(cert)
    cert["mac"]=mac_payload(cert,key)
    return cert

def _parse_time(s: str):
    return datetime.fromisoformat(s.replace("Z","+00:00"))

def verify_authenticated(cert: Dict[str, Any], context: RuntimeContext, key: bytes,
                         used_nonces: Optional[Set[str]]=None,
                         consume_nonce: bool=True) -> Tuple[bool, Optional[str]]:
    if cert.get("issuer") not in ALLOWED_ISSUERS:
        return False, RejectReason.UNAUTHORIZED_ISSUER.value
    if not hmac.compare_digest(str(cert.get("mac","")), mac_payload(cert,key)):
        return False, RejectReason.INVALID_SIGNATURE.value
    if cert.get("workflow_id") != context.workflow_id:
        return False, RejectReason.WRONG_WORKFLOW.value
    if cert.get("execution_id") != context.execution_id:
        return False, RejectReason.WRONG_EXECUTION.value
    if cert.get("source_runtime") != context.source_runtime or cert.get("target_runtime") != context.target_runtime:
        return False, RejectReason.WRONG_RUNTIME.value
    if cert.get("contract_hash") != context.contract_hash:
        return False, RejectReason.INVALID_CERTIFICATE.value
    try:
        if _parse_time(cert["expires_at"]) <= datetime.now(timezone.utc):
            return False, RejectReason.EXPIRED_CERTIFICATE.value
    except Exception:
        return False, RejectReason.INVALID_CERTIFICATE.value
    if used_nonces is not None:
        nonce=str(cert.get("nonce",""))
        if nonce in used_nonces:
            return False, RejectReason.NONCE_REUSE.value
        if consume_nonce:
            used_nonces.add(nonce)
    return True, None

def verify_hash_only(cert: Dict[str, Any], context: RuntimeContext, used_nonces=None,
                     consume_nonce=True) -> Tuple[bool, Optional[str]]:
    """Unkeyed control. Detects accidental mutation, not an attacker who can rehash."""
    if cert.get("digest") != digest_payload(cert):
        return False, RejectReason.INVALID_CERTIFICATE.value
    # Intentionally no issuer authentication and weak/no contextual policy.
    return True, None
