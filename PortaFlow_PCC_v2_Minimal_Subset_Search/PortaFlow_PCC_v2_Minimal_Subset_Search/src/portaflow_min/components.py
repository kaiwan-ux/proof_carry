from __future__ import annotations
from itertools import combinations

COMPONENTS = ("progress", "history", "frontier", "obligations", "receipts", "contract")

def all_subsets():
    for n in range(len(COMPONENTS)+1):
        for c in combinations(COMPONENTS, n):
            yield tuple(c)

def subset_key(parts):
    parts=tuple(sorted(parts, key=COMPONENTS.index))
    return "none" if not parts else "+".join(parts)
