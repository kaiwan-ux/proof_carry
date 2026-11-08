from __future__ import annotations
import hashlib,uuid
from .crypto import sign_body

def issue_certificate(*,issuer_id,execution_id,case_id,workflow_spec_hash,contract_hash,source_runtime,target_runtime,fact_type,subject,value,evidence,issued_at,expires_at,nonce=None,private_key=None):
    body={
      'cert_version':'1.0','certificate_id':str(uuid.uuid5(uuid.NAMESPACE_URL,f'{execution_id}|{fact_type}|{subject}|{nonce or "auto"}')),
      'issuer_id':issuer_id,'execution_id':execution_id,'case_id':case_id,'workflow_spec_hash':workflow_spec_hash,'contract_hash':contract_hash,
      'source_runtime':source_runtime,'target_runtime':target_runtime,'fact_type':fact_type,'subject':subject,'value':value,'evidence':evidence or {},
      'issued_at':int(issued_at),'expires_at':int(expires_at),'nonce':nonce or hashlib.sha256(f'{execution_id}|{fact_type}|{subject}|{value}'.encode()).hexdigest()[:32],
      'signature_alg':'Ed25519'
    }
    body['signature']=sign_body(body,private_key)
    return body
