# Reproduction

## Environment

Python 3.11 or later, `numpy`, `matplotlib` (3.10 tested). No other dependency. Each script reads only `source_data/` (and `figures/cloud_umap_points.npz` for Figure 2), checks the counts it depends on, and writes to `figures/` or `tables/`.

```
python make_figure2_main_results.py
python make_figure3_area_year.py
python make_figure4_network.py
python make_supplementary_figure_s1.py
python make_supplementary_figure_s2.py
python make_supplementary_figure_s3.py
python make_supplementary_tables.py
```

Figure 1 (study design) is drawn by hand and has no script. Filenames retain earlier numbering: `make_figure4_network.py` produces manuscript Figure 3, and `make_figure3_area_year.py` produces manuscript Figure 4.

## Source data

| File | Used in |
|---|---|
| `SourceData_Figure2.csv` | Primary adjusted means and contrasts (3,818,173 papers, 20,203 journals); Figure 2e |
| `SourceData_Figure2_Years.csv` | Contrast by publication year; Results: publication years and research areas |
| `SourceData_Figure2_CloudLeaves.csv`, `SourceData_Figure2_CloudAreas.csv` | Counts behind the title-content map (1,000 topics; 32 clusters); Figure 2a |
| `SourceData_Figure2_Corridors.csv` | Eight outcome-blind journal pairs; Figure 2f, Figure S3 |
| `SourceData_Figure3_AreaYear.csv` | Research area × publication year cells; Figure 4 |
| `SourceData_Figure3_metrics.csv` | Three network summaries; Figure 3c |
| `SourceData_Figure3_nodes.csv`, `SourceData_Figure3_edges.csv` | Node and edge tables of the citation network; kept for provenance, not read by the current scripts |
| `SourceData_Figure4_DistanceEnrichment.csv` | Enrichment by title-content distance; Figure 3a |
| `SourceData_Figure4_estimates.csv`, `SourceData_Figure4_same_author.csv` | Sensitivity and identification-boundary estimates; Table S3 |
| `SourceData_Figure1.csv` | Journal-scope distribution, split-half reliability, and convergent validity; Methods text (Figure 1 is drawn by hand) |
| `SourceData_ED1_cohort_coverage.csv` | Cohort and citation accounting; Figure S1 |
| `SourceData_ED2_propensity_candidates.csv`, `SourceData_ED2_propensity_bins.csv`, `SourceData_ED2_balance.csv` | Propensity candidates, common support, covariate balance; Tables S1–S2, Figure S2 |
| `SourceData_ED3_network_edges.csv` | Standardized 32 × 32 citation-flow matrices for both journal groups; Figure 2c, Figure 3b |
| `SourceData_ED3_lodo.csv`, `SourceData_ED3_sensitivities.csv` | Leave-one-area-out, winsorized, and regenerated-fit estimates; Figure 3c, Table S3 |
| `SourceData_ED4_nodes.csv` | Node positions on the title-content map; Figure 3b |
| `SourceData_ED4_corridors.csv` | Earlier four-pair corridor table, superseded by `SourceData_Figure2_Corridors.csv`; kept for provenance |
| `SourceData_Radial_AreaOrder.csv`, `SourceData_Radial_CitationBackbone.csv`, `SourceData_Radial_LeafScope.csv` | Area order, backbone edges, and topic-level scope from an earlier layout of Figure 2c; kept for provenance |
| `SourceData_Hierarchy_Areas.csv` | Display names of the 31 research areas plus the Mixed records cluster |
| `SourceData_MixedRecordsDiagnostics.csv` | Audit of the Mixed records cluster; Supplementary text |
| `round2_score_diagnostics.csv` | Four aggregate rows: AIPW and outcome-model-only estimates, in the regenerated sample and after excluding papers dated 1 January; Supplementary results |
| `news_*.csv` | Tracked-web-page analysis; Supplementary results (numbers reported in text, no figure) |
| `case_selection.csv`, `journal_corridors.csv` | Journal-pair selection inputs |
| `source_data_manifest.csv` | SHA-256, row count, originating analysis commit, and display mapping for every `SourceData_*.csv` and `round2_score_diagnostics.csv` |
| `figures/cloud_umap_points.npz` | 1,219,650 display points (x, y, area, status) for Figure 2a |

## Vocabulary

Broader-scope and narrower-scope journals are the bottom and top quartiles of the journal scope score within each title-content topic group and publication year. Column names `broad` and `specialized` in some tables denote the same two groups. The 32 title-based clusters are 31 named research areas plus one Mixed records cluster (`qwen_macro` = 18).

In `round2_score_diagnostics.csv`, `near` means same-topic citations and `distant` means citations from another research area. Its four rows describe the regenerated fit, not a replacement for the primary estimate. Source data retain full numerical precision; figures and tables round values for readability.

## Underlying data

OpenAlex snapshot of 26 June 2026 (https://openalex.org); SciSciNet v2 for the tracked-web-page analysis. Paper-level extracts and title embeddings can be recomputed from OpenAlex with the models named in the Methods (SPECTER2, Qwen3-Embedding-0.6B).

The commands above reproduce figures and tables from aggregate inputs. They do not rerun cohort construction, language-model inference, or causal estimation; that upstream code is not part of this release.
