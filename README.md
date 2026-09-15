# reach

Data and figure code for the manuscript *Journal scope and the reach of scientific work*.

This repository contains aggregate results and code for drawing the figures and generating the tables. Paper-level records and the upstream analysis pipeline are not included; the analyses use the OpenAlex snapshot of 26 June 2026 and, for one supplementary analysis, SciSciNet v2.

## Reproduction

Python 3.11 or later with `numpy` and `matplotlib`. See [REPRODUCTION.md](REPRODUCTION.md) for the file inventory and the commands that regenerate each figure and table.

## Follow-up source data

| File | Contents |
|---|---|
| `source_data/SourceData_Decomposition.csv` | 123 aggregate rows: cross-area citation decomposition, other-area counts, ten modifier tests, scope-separation contrasts, within-comparison-set correlations, a 2015 ten-year preview, and a two-hop trial |

This table adds completed follow-up results; it does not replace the primary estimate in `SourceData_Figure2.csv` (3,818,173 papers from 20,203 journals). No models were fitted for this export. The existing figures have not been changed to incorporate it.

Select rows by **`analysis`, `outcome`, and `scale` together**, not by outcome alone. `mean_specialized` denotes the narrower-scope group. Every row identifies its originating aggregate file in `origin`; these paths identify internal analysis artifacts, not files included in this public repository.

| `analysis` | Population and role |
|---|---|
| `aipw`, `ipw`, `outcome_model_only` | Same downstream comparison sample: 3,827,491 papers, 20,215 journals. Citation count, receipt probability, citing-area breadth, and conditional count. `decomp_*` rows are exact AIPW aliases for plotting, not additional estimates. |
| `aipw_modifiers` | Same downstream sample; ten global tests, each with its original P value and ten-test-family BH q value. These test heterogeneity of the saved far/near contrast. |
| `aipw_scope_gap_1`, `_2`, `_3` | Respective subsets of 1,341,573, 1,354,905, and 1,131,013 papers. They reuse the earlier paired near/far scores, not the later count-outcome models. |
| `aipw_scope_endpoints` | Joint large-minus-small contrast within the 3,827,491-paper journal universe; journals may contribute to both strata. |
| `within_choice_set` | `n` is 5,872 topic-by-year comparison sets, covering all 3,827,491 downstream papers. Mean within-set Spearman correlations weighted by set paper count; not IPW correlations. |
| `ipw_2015` | Existing 2015-cohort preview: 596,758 papers, 11,635 journals. First-five-year, sixth-to-tenth-year, and cumulative-ten-year quantities; not AIPW. |
| `ipw_twohop` | 10,000 sampled 2015 root papers, 4,147 journals. Continuation per eligible first-hop citing paper, not an individual-root continuation probability. |

Probability means and absolute differences are fractions, not percentages or percentage points. Count means are per paper; `far_given_any_far` means are per paper receiving at least one cross-area citation. `n_macros_other_named31` excludes the study paper's own area and Mixed records; `n_macros_cited_named31` includes the own area; `far_all32` includes all 32 areas. These outcomes are not successive distance thresholds.

For each group, conditional count equals cross-area mean divided by receipt probability. Between groups, `decomp_total = decomp_entry + decomp_intensity` holds on the **log scale**, not after converting the three components separately to percentages. `decomp_contrast` is intensity minus entry on the log scale, with their covariance included in both stored interval methods.

`support` is retained/eligible paper count for full or scope-stratum comparisons, and comparison-set coverage for correlations. It is blank for the fixed 2015 and two-hop populations, where a comparable retention fraction is not provided. Empty SE/CI cells mean no interval was estimated or the statistic is a P/q value; they are not zero. The 11 earlier outcome-model-only rows have point estimates only. New other-area outcome-model-only intervals condition on saved predictions and omit model-fitting uncertainty. AIPW and IPW intervals use journal-cluster influence functions and 500 shared-journal multipliers.

`window_definition` records literal citation-date bounds for the 13 `ipw_2015` rows; it is blank for other analysis blocks. Here `t0` is the study paper's publication date, the lower bound is inclusive, and the upper bound is exclusive. `theta_y1_5` uses `[t0, t0+60 months)`, `theta_y6_10` uses `[t0+60 months, t0+120 months)` (no first-five-year citations), and `theta_y1_10` uses `[t0, t0+120 months)` cumulatively. The paired `theta_120_minus_60` estimate compares **cumulative years 1–10 with years 1–5**, not years 6–10 with years 1–5. Pairing determines the covariance in its interval; its point estimate is still the difference of those two population contrasts. This metadata addition changes no numerical cell.

The full-sample citation-use measures and decomposition components use the same downstream support. The original primary far/near contrast remains unchanged. The new other-area endpoint required ten Poisson fits, all of which reached the 500-tree cap; the released estimates retain the observed dependence on outcome adjustment rather than selecting among methods.

## License

Code: MIT. Data: CC BY 4.0.

## Contact

Haining Wang, Indiana University, hw56@iu.edu
