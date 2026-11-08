from __future__ import annotations
import hashlib, json
from .models import SemanticCertificate

def _hash_evidence(fact_type,subject,value,scope,evidence):
    body={"fact_type":fact_type,"subject":subject,"value":value,"scope":scope,"evidence":evidence}
    return hashlib.sha256(json.dumps(body,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

def issue_certificate(case_id:str,fact_type:str,subject:str,value,scope:str,evidence:dict,issuer="crossresumebench_witness"):
    digest=_hash_evidence(fact_type,subject,value,scope,evidence)
    cid=hashlib.sha256(f"{case_id}|{fact_type}|{subject}|{scope}|{digest}".encode()).hexdigest()[:20]
    return SemanticCertificate(cid,fact_type,subject,value,scope,evidence,issuer,digest)

def verify_certificate(cert:dict)->bool:
    try:
        return cert.get("evidence_hash")==_hash_evidence(cert["fact_type"],cert["subject"],cert.get("value"),cert["scope"],cert.get("evidence",{}))
    except Exception:
        return False
