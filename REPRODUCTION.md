# Reproduction

## Environment

Python 3.11 or later, `numpy`, `matplotlib`, and `scipy`. SciPy provides the pooled-profile clustering used to order the Figure 2 matrix. Each figure script reads `source_data/` (and `figures/cloud_umap_points.npz` for Figures S5–S6), checks the counts it depends on, and writes to `figures/` or `tables/`. These commands only redraw stored results; they do not fit models.

```
python make_figure2_results.py
python make_figure3_mechanism.py
python make_figure4_generality.py
python make_supplementary_figure_s1.py
python make_supplementary_figure_s2.py
python make_supplementary_figure_s3.py
python make_figure3_area_year.py
python make_supplementary_figure_s5_map.py
python make_supplementary_figure_s6_network.py
python make_supplementary_tables.py
python make_supplementary_tables_decomposition.py
python export_display_data.py
python validate_manuscript.py --source-only
```

Figure 1 is drawn by hand and has no script. The commands above produce the current figures; earlier-layout scripts and outputs remain for provenance but are not the current display items. `make_figure3_area_year.py` produces Supplementary Figure S4. Figure 2 combines the primary means, a 31-by-31 matrix of named areas, and the per-area forest. The full 32-by-32 matrices, including Mixed records, remain in `SourceData_ED3_network_edges.csv` as 1,024 unique ordered pairs with a column for each group.

Figure 3 uses the full downstream decomposition, distance-enrichment curve, and network summaries. Panel c converts stored log2 share ratios to percentage differences. Panel d divides absolute differences and their stored confidence limits by the saved broader-scope mean. Those rescaled limits are not independently estimated mean-ratio intervals. Figure 4 combines a 31-by-6 area-year heatmap, the six-year forest, and the 2015-cohort preview. Its panel c has 596,758 papers, not the full downstream population; the literal window definitions are included in its CSV. The cumulative-ten-year-minus-five-year annotation is not a test of the late-only versus early-only points.

The display-data archive has exactly ten CSVs. Multiple panels within an item share a CSV with a `panel` column; empty cells indicate columns that do not apply to that panel. Figure 1 is header-only because it has no empirical plotted values. Figure S5 contains the exact 420,000 points selected by the current plotting script (seed 20260915), plus 31 label anchors; the NPZ retains all 1,219,650 projected display papers. Figure S6 uses medians of comparison-status points within the map's central 99% range for its 31 nodes, and the 89 saved named-area backbone arcs. The archive contains these coordinates and edge differences, not a newly estimated network.

Area and year estimates pool papers, not heatmap cells. The precision funnel remains in Supplementary Figure S4.

Heatmap labels are percentage changes rounded to whole numbers. The asterisk marks an existing Benjamini--Hochberg-adjusted q value below 0.05; the correction covers all 164 estimable area-year cells, including six Mixed records cells omitted from the display. The marked cell is Orthopaedics & sports medicine in 2019 (q = 0.0111). No p or q values are recomputed for the figure.

## Source data

| File | Used in |
|---|---|
| `SourceData_Figure2.csv` | Primary adjusted means and contrasts (3,818,173 papers, 20,203 journals); Figure 2a |
| `SourceData_Decomposition.csv` | Figure 3a–b and Figure 4c; completed follow-up estimates with population and window definitions documented in the README |
| `SourceData_ReportedFacts.csv` | Six locked values: comparison-set count and two correlations, citation-link and citing-paper counts, reference-side ratio |
| `SourceData_Figure2_Years.csv` | Contrast by publication year; Figure 4b |
| `SourceData_Figure2_CloudLeaves.csv`, `SourceData_Figure2_CloudAreas.csv` | Counts behind the title-content map (1,000 topics; 32 clusters); Figure S5 label positions |
| `SourceData_Figure2_Corridors.csv` | Eight outcome-blind journal pairs; Figure S3 |
| `SourceData_Figure3_AreaYear.csv` | Research area × publication year cells; Figure 4a and Figure S4 |
| `SourceData_Figure4_Areas.csv` | All 31 named research-area contrasts; Figure 2c |
| `SourceData_Figure3_metrics.csv` | Three network summaries; Figure 3d |
| `SourceData_Figure3_nodes.csv`, `SourceData_Figure3_edges.csv` | Node and edge tables of the citation network; kept for provenance, not read by the current scripts |
| `SourceData_Figure4_DistanceEnrichment.csv` | Enrichment by title-content distance; Figure 3c |
| `SourceData_Figure4_estimates.csv`, `SourceData_Figure4_same_author.csv` | Sensitivity and identification-boundary estimates; Table S3 |
| `SourceData_Figure1.csv` | Journal-scope distribution, split-half reliability, and convergent validity; Methods text (Figure 1 is drawn by hand) |
| `SourceData_ED1_cohort_coverage.csv` | Cohort and citation accounting; Figure S1 |
| `SourceData_ED2_propensity_candidates.csv`, `SourceData_ED2_propensity_bins.csv`, `SourceData_ED2_balance.csv` | Propensity candidates, common support, covariate balance; Tables S1–S2, Figure S2 |
| `SourceData_ED3_network_edges.csv` | Standardized 32 × 32 citation-flow matrices for both journal groups; Figure 2b and Figure S6 |
| `SourceData_ED3_lodo.csv`, `SourceData_ED3_sensitivities.csv` | Leave-one-area-out, winsorized, and regenerated-fit estimates; Figure 3d and Table S3 |
| `SourceData_ED4_nodes.csv` | Earlier network node positions; retained for provenance, not read by the current figures |
| `SourceData_ED4_corridors.csv` | Earlier four-pair corridor table, superseded by `SourceData_Figure2_Corridors.csv`; kept for provenance |
| `SourceData_Radial_AreaOrder.csv`, `SourceData_Radial_CitationBackbone.csv`, `SourceData_Radial_LeafScope.csv` | Area order, backbone edges, and topic-level scope from an earlier layout of Figure 2c; kept for provenance |
| `SourceData_Hierarchy_Areas.csv` | Display names of the 31 research areas plus the Mixed records cluster |
| `SourceData_MixedRecordsDiagnostics.csv` | Audit of the Mixed records cluster; Supplementary text |
| `round2_score_diagnostics.csv` | Four aggregate rows: AIPW and outcome-model-only estimates, in the regenerated sample and after excluding papers dated 1 January; Supplementary results |
| `news_*.csv` | Tracked-web-page analysis; Supplementary results (numbers reported in text, no figure) |
| `case_selection.csv`, `journal_corridors.csv` | Journal-pair selection inputs |
| `source_data_manifest.csv` | SHA-256, row count, originating analysis commit, and display mapping for every `SourceData_*.csv` and `round2_score_diagnostics.csv` |
| `figures/cloud_umap_points.npz` | 1,219,650 projected display points (x, y, area, status); current Figures S5–S6 select subsets as described above |
| `Source_Data.zip` | One current-display CSV per Figure 1–4 and Supplementary Figure S1–S6; regenerated by `export_display_data.py` |

## Vocabulary

Broader-scope and narrower-scope journals are the bottom and top quartiles of the journal scope score within each title-content topic group and publication year. Column names `broad` and `specialized` in some tables denote the same two groups. The 32 title-based clusters are 31 named research areas plus one Mixed records cluster (`qwen_macro` = 18).

In `round2_score_diagnostics.csv`, `near` means same-topic citations and `distant` means citations from another research area. Its four rows describe the regenerated fit, not a replacement for the primary estimate. Source data retain full numerical precision; figures and tables round values for readability.

## Underlying data

OpenAlex snapshot of 26 June 2026 (https://openalex.org); SciSciNet v2 for the tracked-web-page analysis. Paper-level extracts and title embeddings can be recomputed from OpenAlex with the models named in the Methods (SPECTER2, Qwen3-Embedding-0.6B).

The commands above reproduce figures and tables from aggregate inputs. They do not rerun cohort construction, language-model inference, or causal estimation; that upstream code is not part of this release.
