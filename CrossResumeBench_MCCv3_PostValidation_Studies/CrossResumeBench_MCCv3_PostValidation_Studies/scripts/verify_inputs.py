from _bootstrap import *
import json
from studies.common import verify_passed_holdout_inputs
if __name__=='__main__': print(json.dumps(verify_passed_holdout_inputs(),indent=2))
