from pathlib import Path
import json,sys,platform,importlib.metadata as im
ROOT=Path(__file__).resolve().parents[1]; names=['langgraph','crewai','agent-framework-core','pandas','jsonschema','pydantic']; v={n:(im.version(n) if n in {d.metadata['Name'] for d in im.distributions() if d.metadata.get('Name')} else None) for n in names}; out={'python':sys.version,'platform':platform.platform(),'packages':v}; (ROOT/'results'/'ENVIRONMENT.json').write_text(json.dumps(out,indent=2)); print(json.dumps(out,indent=2))
