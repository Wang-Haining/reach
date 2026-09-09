# Journal scope and the reach of scientific work — data and figure code

Aggregate data and plotting code for the manuscript *Journal scope and the reach of
scientific work* (Haining Wang, Indiana University School of Medicine). Every number
printed in the manuscript and its Supplementary Information is computed from the tables
in `source_data/`; `validate_manuscript.py` in the manuscript repository asserts them
against these files.

The underlying paper-level data are the OpenAlex snapshot of 26 June 2026
(https://openalex.org) and, for the tracked-web-page analysis, SciSciNet v2. Paper-level
extracts and title embeddings are not redistributed; they can be recomputed from OpenAlex
with the models named in the Methods (SPECTER2, Qwen3-Embedding-0.6B).

## Layout

| Path | Contents |
|---|---|
| `source_data/SourceData_Figure1.csv` | Figure 1: journal-scope histogram, split-half reliability, convergent validity, research-area estimates |
| `source_data/SourceData_Figure2.csv` | Primary adjusted means and contrasts (3,818,173 papers, 20,203 journals) |
| `source_data/SourceData_Figure2_Years.csv` | Contrast by publication year |
| `source_data/SourceData_Figure2_CloudLeaves.csv`, `..._CloudAreas.csv` | Counts behind the title-content map (1,000 topics; 32 clusters) |
| `source_data/SourceData_Figure2_Corridors.csv` | Eight outcome-blind journal pairs (Figure 2f, Supplementary Figure S3) |
| `source_data/SourceData_Figure3_AreaYear.csv` | Research-area × publication-year cells (Figure 3) |
| `source_data/SourceData_Figure3_metrics.csv`, `..._nodes.csv`, `..._edges.csv` | Network summaries and node layout |
| `source_data/SourceData_Figure4_DistanceEnrichment.csv` | Enrichment by title-content distance (Figure 4a) |
| `source_data/SourceData_Figure4_estimates.csv`, `..._same_author.csv` | Identification-boundary estimates (Table S3) |
| `source_data/SourceData_ED1_cohort_coverage.csv` | Cohort and citation accounting (Figure S1) |
| `source_data/SourceData_ED2_*.csv` | Propensity candidates, common support, covariate balance (Table S1, Table S2, Figure S2) |
| `source_data/SourceData_ED3_network_edges.csv` | Standardized 32 × 32 citation-flow matrices for both journal groups (Figure 2c, Figure 4b) |
| `source_data/SourceData_ED3_lodo.csv`, `..._sensitivities.csv` | Leave-one-area-out estimates; winsorized and regenerated-fit estimates |
| `source_data/SourceData_ED4_nodes.csv`, `..._corridors.csv` | Node positions on the title-content map; earlier four-pair corridor table (superseded by `SourceData_Figure2_Corridors.csv`) |
| `source_data/SourceData_Hierarchy_Areas.csv` | Display names of the 31 research areas |
| `source_data/SourceData_MixedRecordsDiagnostics.csv` | Audit of the Mixed records cluster |
| `source_data/news_*.csv` | Tracked-web-page analysis (Supplementary results) |
| `source_data/case_selection.csv`, `journal_corridors.csv` | Journal-pair selection inputs |
| `source_data/source_data_manifest.csv` | SHA-256, row count, and figure use of every `SourceData_*.csv` |
| `figures/cloud_umap_points.npz` | 1,219,650 display points (x, y, area, status) for the map in Figure 2a |
| `figures/*.pdf`, `figures/*.png` | Rendered figures |
| `tables/*.tex` | Supplementary Tables S1–S3 as generated |
| `make_*.py` | Scripts that draw every figure and table from `source_data/` (Python 3.11, matplotlib 3.10, numpy) |

## Reproducing the figures

```
python make_figure2_main_results.py
python make_figure3_area_year.py
python make_figure4_network.py
python make_supplementary_figure_s1.py
python make_supplementary_figure_s2.py
python make_supplementary_figure_s3.py
python make_supplementary_tables.py
```

Each script reads only `source_data/` (and `figures/cloud_umap_points.npz` for Figure 2),
checks the counts it depends on, and writes to `figures/` or `tables/`.

## Vocabulary

Broader-scope and narrower-scope journals are the bottom and top quartiles of the journal
scope score within each title-content topic group and publication year. The column names
`broad`/`specialized` in some tables are the same two groups. The 32 title-based clusters
are 31 named research areas plus one Mixed records cluster (`qwen_macro` = 18).

## License

Data: CC BY 4.0. Code: MIT.
