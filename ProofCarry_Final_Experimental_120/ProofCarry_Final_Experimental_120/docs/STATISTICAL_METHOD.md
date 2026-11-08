# Statistical Method

The primary statistical unit is the **base semantic case**. Runtime pairs and evidence variants generated from one base case are aggregated within that case and are not treated as independent samples.

For pairwise method comparisons the analysis exports:

1. base-case mean outcome rates;
2. paired mean difference;
3. case-block bootstrap 95% confidence interval (10,000 resamples);
4. paired Wilcoxon signed-rank p-value;
5. Holm-adjusted p-value across comparisons;
6. rank-biserial effect size.

This follows the previously established case/block-level approach and avoids artificially inflating sample size with correlated runtime-pair repetitions.
