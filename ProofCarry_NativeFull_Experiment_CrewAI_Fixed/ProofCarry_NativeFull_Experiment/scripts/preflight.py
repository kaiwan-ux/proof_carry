from __future__ import annotations
import argparse,importlib,importlib.metadata,platform,sys
REQ={'langgraph':'1.2.11','crewai':'1.15.17','agent-framework-core':'1.15.0'}
ap=argparse.ArgumentParser(); ap.add_argument('--allow-version-mismatch',action='store_true'); a=ap.parse_args()
print('Python',sys.version.replace('\n',' ')); print('Platform',platform.platform())
fail=[]
if not ((3,12) <= sys.version_info[:2] < (3,14)): fail.append(f'Python {sys.version_info.major}.{sys.version_info.minor} is outside >=3.12,<3.14')
for dist,expected in REQ.items():
    try: got=importlib.metadata.version(dist); print(dist,got,'expected',expected); 
    except Exception as e: got=None; print(dist,'MISSING',e)
    if got!=expected: fail.append(f'{dist}: expected {expected}, got {got}')
for dist in ['cryptography','scipy','pandas','psutil','jsonschema','pydantic','pytest','tabulate']:
    try: print(dist,importlib.metadata.version(dist))
    except Exception as e: fail.append(f'{dist} missing: {e}')
if fail:
    print('\nPRECHECK ISSUES:'); [print('-',x) for x in fail]
    if not a.allow_version_mismatch: raise SystemExit(2)
print('Preflight PASS' if not fail else 'Preflight completed with allowed mismatches')
