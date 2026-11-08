from __future__ import annotations
import base64,json,hashlib
from dataclasses import dataclass
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey,Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

def canonical_bytes(obj:dict)->bytes:
    return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=True,default=str).encode('utf-8')
def deterministic_test_private_key()->Ed25519PrivateKey:
    # BENCHMARK-ONLY deterministic key; never use this seed in deployment.
    seed=hashlib.sha256(b'CrossResumeBench-ProofCarry-104-benchmark-key-v1').digest()
    return Ed25519PrivateKey.from_private_bytes(seed)
def public_key_b64(private=None)->str:
    from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
    private=private or deterministic_test_private_key()
    return base64.b64encode(private.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)).decode()
def sign_body(body:dict,private=None)->str:
    private=private or deterministic_test_private_key(); return base64.b64encode(private.sign(canonical_bytes(body))).decode()
def verify_body(body:dict,signature_b64:str,public_b64:str)->bool:
    try:
        pub=Ed25519PublicKey.from_public_bytes(base64.b64decode(public_b64)); pub.verify(base64.b64decode(signature_b64),canonical_bytes(body)); return True
    except (InvalidSignature,ValueError,TypeError): return False

class ReplayCache:
    def __init__(self): self._seen=set()
    def seen(self,issuer,nonce): return (issuer,nonce) in self._seen
    def mark(self,issuer,nonce): self._seen.add((issuer,nonce))
