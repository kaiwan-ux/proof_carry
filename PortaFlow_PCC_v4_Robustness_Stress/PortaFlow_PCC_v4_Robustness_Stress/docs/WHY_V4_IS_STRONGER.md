# Why v4 is stronger

Earlier experiments established problem existence, PCC sufficiency, minimal subsets, and held-out workflow generalization. v4 attacks a different failure mode: **evidence quality**. Real distributed systems may deliver duplicate observations, reorder logs, lose events, or present conflicting commitment evidence. A useful continuation mechanism must normalize benign corruption and fail closed under semantic uncertainty rather than maximizing completion at the cost of duplicate external effects.
