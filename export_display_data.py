#!/usr/bin/env python3
"""Package the values drawn in the current four main and six supplementary figures.

One CSV per display item. Only selection, layout, and plotted-scale arithmetic;
no model fitting. Original SourceData filenames and estimates remain unchanged.
"""
import csv
import io
import math
import zipfile
from pathlib import Path

import numpy as np
from scipy.cluster.hierarchy import leaves_list, linkage
from scipy.spatial.distance import squareform

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "source_data"
OUT = {f"Figure {i}": [] for i in range(1, 5)}
OUT.update({f"Supplementary Figure S{i}": [] for i in range(1, 7)})


def read(name):
    with (DATA / name).open(newline="") as f:
        return list(csv.DictReader(f))


def add(display, panel, origin, **values):
    OUT[display].append(dict(panel=panel, **values, origin=origin))


def take(display, panel, name, columns, predicate=lambda r: True):
    for row in read(name):
        if predicate(row):
            add(display, panel, name, **{k: row[k] for k in columns.split()})


def pct(x):
    return 100 * math.expm1(float(x))


def ratio(display, panel, name, row, transform=pct, **extra):
    add(display, panel, name, **extra, estimate=transform(row["estimate"]),
        ci_low=transform(row["ci_low"]), ci_high=transform(row["ci_high"]))


primary = read("SourceData_Figure2.csv")
for r in primary:
    if r["outcome"] in ("far", "near", "intermediate"):
        add("Figure 2", "a", "SourceData_Figure2.csv", outcome=r["outcome"],
            **{k: r[k] for k in ("mean_broad", "mean_specialized", "estimate", "ci_low", "ci_high")},
            unit="citations per paper")
    if r["outcome"] == "far_to_near_routing":
        ratio("Figure 2", "a annotation", "SourceData_Figure2.csv", r, outcome=r["outcome"], unit="percent")
p = {r["outcome"]: r for r in primary}
for arm in ("broad", "specialized"):
    add("Figure 2", "a annotation", "SourceData_Figure2.csv", outcome="other-area per same-topic citation",
        arm=arm, estimate=float(p["far"]["mean_" + arm]) / float(p["near"]["mean_" + arm]), unit="ratio")

edges = read("SourceData_ED3_network_edges.csv")
assert len(edges) == 1024
profile = np.zeros((32, 32))
for r in edges:
    profile[int(r["source_internal_domain_id"]), int(r["citing_internal_domain_id"])] = float(r["pooled_standardized_share"])
profile /= profile.sum(axis=1, keepdims=True)
order = [int(m) for m in leaves_list(linkage(squareform(1 - np.corrcoef(profile), checks=False), method="average")) if m != 18]
for r in edges:
    a, b = int(r["source_internal_domain_id"]), int(r["citing_internal_domain_id"])
    if 18 not in (a, b):
        add("Figure 2", "b", "SourceData_ED3_network_edges.csv", source_area=r["source_domain"],
            citing_area=r["citing_domain"], row=order.index(a), column=order.index(b),
            estimate=100 * float(r["standardized_share_difference"]), unit="percentage points of standardized flow")
take("Figure 2", "c", "SourceData_Figure4_Areas.csv", "display_label estimate ci_low ci_high")

decomp = read("SourceData_Decomposition.csv")
for r in decomp:
    if r["analysis"] == "aipw":
        if r["outcome"] in ("any_far_all32", "n_macros_other_named31", "far_all32") and r["scale"] == "log_mean_ratio":
            ratio("Figure 3", "a", "SourceData_Decomposition.csv", r, outcome=r["outcome"], unit="percent")
        if r["outcome"] in ("decomp_total", "decomp_entry", "decomp_intensity"):
            add("Figure 3", "b", "SourceData_Decomposition.csv", outcome=r["outcome"], estimate=pct(r["estimate"]), unit="percent")
        if r["outcome"] == "decomp_contrast":
            ratio("Figure 3", "b annotation", "SourceData_Decomposition.csv", r, outcome=r["outcome"], unit="percent")
    if r["analysis"] == "ipw_2015" and r["outcome"] in ("theta_y1_5", "theta_y6_10", "theta_120_minus_60"):
        ratio("Figure 4", "c annotation" if r["outcome"] == "theta_120_minus_60" else "c",
              "SourceData_Decomposition.csv", r, outcome=r["outcome"], unit="percent",
              window_definition=r["window_definition"], n=r["n"], journals=r["journals"])
for r in read("SourceData_Figure4_DistanceEnrichment.csv"):
    add("Figure 3", "c", "SourceData_Figure4_DistanceEnrichment.csv", bin=r["bin"],
        distance_midpoint=(float(r["distance_lo"]) + float(r["distance_hi"])) / 2,
        estimate=100 * math.expm1(math.log(2) * float(r["log2_ratio_narrow_over_broad"])),
        ci_low=100 * math.expm1(math.log(2) * float(r["ci_low"])),
        ci_high=100 * math.expm1(math.log(2) * float(r["ci_high"])),
        raw_edges=int(r["raw_edges_broad"]) + int(r["raw_edges_narrow"]), unit="percent")
metrics = {r["metric"]: r for r in read("SourceData_Figure3_metrics.csv")}
for key, r in metrics.items():
    add("Figure 3", "d", "SourceData_Figure3_metrics.csv", metric=key,
        estimate=float(r["contrast_specialized_minus_broad"]),
        ci_low=float(r["ci_low"]), ci_high=float(r["ci_high"]),
        unit="absolute difference in graph metric")
for r in read("SourceData_ED3_lodo.csv"):
    add("Figure 3", "d leave-one-area-out", "SourceData_ED3_lodo.csv", metric=r["metric"],
        omitted_area=r["omitted_source_domain"],
        estimate=float(r["contrast_specialized_minus_broad"]), unit="absolute difference in graph metric")

cells = [r for r in read("SourceData_Figure3_AreaYear.csv") if r["qwen_macro"] != "18"]
shown = {r["qwen_macro"] for r in cells if r["status"] == "estimated"}
for r in cells:
    vals = dict(area=r["display_label"], year=r["publication_year"], status=r["status"])
    add("Figure 4", "a", "SourceData_Figure3_AreaYear.csv", **vals,
        estimate=pct(r["estimate"]) if r["status"] == "estimated" else "",
        bh_marker=float(r["q_value_bh"]) < 0.05 if r["status"] == "estimated" else "", unit="percent")
    if r["qwen_macro"] in shown:
        add("Supplementary Figure S4", "a", "SourceData_Figure3_AreaYear.csv", **vals,
            estimate=r["estimate"], ci_excludes_zero=(float(r["ci_high"]) < 0 or float(r["ci_low"]) > 0) if r["status"] == "estimated" else "", unit="log ratio-of-ratios")
    if r["status"] == "estimated":
        add("Supplementary Figure S4", "b", "SourceData_Figure3_AreaYear.csv", **vals,
            estimate=r["estimate"], se=r["se"], n=r["n"], ci_low=r["ci_low"], ci_high=r["ci_high"], unit="log ratio-of-ratios")
for r in read("SourceData_Figure2_Years.csv"):
    ratio("Figure 4", "b", "SourceData_Figure2_Years.csv", r, year=r["level"], unit="percent")
add("Supplementary Figure S4", "b reference", "make_figure3_area_year.py#POOLED", estimate=-0.0824527, unit="log ratio-of-ratios")

# Figure S1 prints these saved lineage counts and their arithmetic differences.
counts = dict(original_papers=19896656, scored_papers=15233734, extreme_quartiles=7683322,
              eligible_papers=7617662, eligible_broad=3268625, eligible_narrow=4349037,
              primary_papers=3818173, primary_journals=20203, regenerated_papers=3827491,
              regenerated_broad=1535843, regenerated_narrow=2291648, regenerated_journals=20215)
counts.update(no_score_or_set=counts["original_papers"] - counts["scored_papers"],
              middle_scope=counts["scored_papers"] - counts["extreme_quartiles"],
              title_out_of_distribution=counts["extreme_quartiles"] - counts["eligible_papers"],
              outside_support=counts["eligible_papers"] - counts["primary_papers"])
for key, val in counts.items():
    add("Supplementary Figure S1", "sample flow", "make_supplementary_figure_s1.py#saved_counts", measure=key, value=val, unit="journals" if "journals" in key else "papers")
cov = [r for r in read("SourceData_ED1_cohort_coverage.csv") if r["panel"] == "d"]
for r in cov:
    add("Supplementary Figure S1", "citation accounting", "SourceData_ED1_cohort_coverage.csv", measure=r["measure"], value=r["value"], unit=r["unit"])
add("Supplementary Figure S1", "citation accounting", "SourceData_ED1_cohort_coverage.csv#sum_panel_d", measure="all links", value=sum(int(float(r["value"])) for r in cov), unit="citation edges")
take("Supplementary Figure S2", "a", "SourceData_ED2_propensity_bins.csv", "arm bin_left bin_right density")
balance = [r for r in read("SourceData_ED2_balance.csv") if r["candidate"] == "primary_leaves_63"]
top = sorted((r for r in balance if r["stage"] == "weighted"), key=lambda r: -abs(float(r["smd"])))[:12]
for r in balance:
    if r["stage"] in ("weighted", "raw") and r["covariate"] in {x["covariate"] for x in top}:
        add("Supplementary Figure S2", "b", "SourceData_ED2_balance.csv", stage=r["stage"], covariate=r["covariate"], absolute_smd=abs(float(r["smd"])))
take("Supplementary Figure S3", "a", "SourceData_Figure2_Corridors.csv", "case_rank display_label broad_name narrow_name broad_scope narrow_scope")
take("Supplementary Figure S3", "b", "SourceData_Figure2_Corridors.csv", "case_rank display_label area_n routing_change_percent routing_ci_low_percent routing_ci_high_percent")

pts = np.load(ROOT / "figures/cloud_umap_points.npz")
x, y, macro, status = (pts[k] for k in ("x", "y", "macro", "status"))
assert len(x) == len(y) == len(macro) == len(status) == 1219650
assert np.isfinite(x).all() and np.isfinite(y).all()
keep = np.random.default_rng(20260915).choice(len(x), 420000, replace=False)
for i in keep:
    add("Supplementary Figure S5", "points", "figures/cloud_umap_points.npz", point_index=int(i), x=float(x[i]), y=float(y[i]), qwen_macro=int(macro[i]))
labels = {int(r["qwen_macro"]): r["display_label"] for r in read("SourceData_Hierarchy_Areas.csv")}
for r in read("SourceData_Figure2_CloudAreas.csv"):
    if r["qwen_macro"] != "18":
        add("Supplementary Figure S5", "label anchor", "SourceData_Figure2_CloudAreas.csv;SourceData_Hierarchy_Areas.csv", x=r["umap_x"], y=r["umap_y"], qwen_macro=r["qwen_macro"], area=labels[int(r["qwen_macro"])])
# S6 uses the trimmed, comparison-status subset for node medians, not S5's full-sample medians.
ux, uy = x.astype(float), y.astype(float)
xl, xh = np.percentile(ux, [0.5, 99.5]); yl, yh = np.percentile(uy, [0.5, 99.5])
inside = (ux > xl) & (ux < xh) & (uy > yl) & (uy < yh) & (status != 0)
for r in edges:
    a, b = int(r["source_internal_domain_id"]), int(r["citing_internal_domain_id"])
    if 18 in (a, b) or (a != b and r["plot_edge"] != "True"):
        continue
    vals = dict(source_area=r["source_domain"], citing_area=r["citing_domain"], standardized_share_difference=r["standardized_share_difference"])
    if a == b:
        vals.update(x=float(np.median(ux[inside & (macro == a)])), y=float(np.median(uy[inside & (macro == a)])))
    add("Supplementary Figure S6", "nodes" if a == b else "arcs", "SourceData_ED3_network_edges.csv;figures/cloud_umap_points.npz", **vals)

expected = [0, 998, 123, 195, 20, 104, 16, 327, 420031, 120]
assert [len(v) for v in OUT.values()] == expected, {k: len(v) for k, v in OUT.items()}
archive = ROOT / "Source_Data.zip"
with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for name, records in OUT.items():
        columns = list(dict.fromkeys(k for r in records for k in r)) or ["panel", "value", "origin"]
        buf = io.StringIO(newline="")
        writer = csv.DictWriter(buf, fieldnames=columns, lineterminator="\n")
        writer.writeheader(); writer.writerows(records)
        entry = zipfile.ZipInfo(name + ".csv", date_time=(2026, 9, 15, 0, 0, 0))
        entry.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(entry, buf.getvalue().encode())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for name, records in OUT.items():
        exported = list(csv.DictReader(io.StringIO(z.read(name + ".csv").decode())))
        assert len(exported) == len(records)
        for before, after in zip(records, exported):
            assert all(after[k] == str(v) for k, v in before.items()), (name, before, after)
print({"status": "PASS", "display_rows": {k: len(v) for k, v in OUT.items()},
       "archive_bytes": archive.stat().st_size, "new_estimates": 0})
