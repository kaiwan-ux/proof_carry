# MCC v3 rationale

MCC v2 rejected ambiguous external commitment and semantic completion but often treated a missing retry bound, approval, callback, loop position, branch completion or compensation obligation as if the fact were absent. MCC v3 changes the admissibility rule: the target declares which facts are continuation-critical, and every one must be proven before execution. Complete snapshots are the only way to infer negative membership (for example, "no approval is pending") from absence.
