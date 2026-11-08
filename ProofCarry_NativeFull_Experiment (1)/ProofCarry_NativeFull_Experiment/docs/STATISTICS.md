# Statistical Analysis

- Independent unit: base case (`n=120`).
- Repeated factors: source runtime, target runtime, evidence condition, method.
- Primary safety comparison: case-level unsafe-rate difference.
- Confidence intervals: nonparametric bootstrap resampling base cases as blocks.
- Paired nonparametric tests: Wilcoxon signed-rank when case-level paired differences are non-degenerate.
- Multiple comparisons: Holm correction for the planned method contrasts.
- Performance: report median, p95, and per-stage decomposition; avoid significance claims unless repeated paired timing tests are explicitly run and assumptions are checked.
