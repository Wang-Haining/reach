#!/usr/bin/env python3
"""Figure 4: citation origins in a common comparison population are more locally concentrated
under narrower-scope publication.

a  enrichment of citation flow by title-content distance (1,000 leaf topics)
b  32 x 32 standardized-share difference matrix, areas ordered along the map
c  three network summaries with leave-one-area-out estimates
All panels use the deterministic comparison sample (3,827,491 papers).
"""
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "source_data"
BLUE, RED, INK, GREY = "#2E5C9E", "#B23A2A", "#222222", "#8A8A8A"
NAVY, DEEP_RED, PALE = "#08306B", "#7F0000", "#F7F5F2"
CMAP = LinearSegmentedColormap.from_list("navy_red", [NAVY, "#4A7BB7", PALE, "#C9553D", DEEP_RED])
plt.rcParams.update({"font.family": "Arial", "font.size": 7, "pdf.fonttype": 42, "ps.fonttype": 42,
                     "axes.linewidth": 0.6})


def read(name):
    with (DATA / name).open(newline="") as handle:
        return list(csv.DictReader(handle))


enrich = read("SourceData_Figure4_DistanceEnrichment.csv")
edges = read("SourceData_ED3_network_edges.csv")
nodes = read("SourceData_ED4_nodes.csv")
metrics = read("SourceData_Figure3_metrics.csv")
lodo = read("SourceData_ED3_lodo.csv")
labels = {int(r["qwen_macro"]): r["display_label"] for r in read("SourceData_Hierarchy_Areas.csv")}
labels[18] = "Mixed records"
assert len(enrich) == 17 and len(edges) == 1024 and len(nodes) == 32 and len(lodo) == 96 and len(metrics) == 3

fig = plt.figure(figsize=(7.0, 5.8))
gs = fig.add_gridspec(2, 2, width_ratios=[1.05, 1], height_ratios=[1.35, 0.85], wspace=0.30, hspace=0.38,
                      left=0.105, right=0.93, top=0.93, bottom=0.08)
ax_a = fig.add_subplot(gs[0, 0]); ax_b = fig.add_subplot(gs[0, 1]); ax_c = fig.add_subplot(gs[1, :])

# ---------------------------------------------------------------- a: enrichment by distance
same = enrich[0]
rest = enrich[1:]
mid = np.array([(float(r["distance_lo"]) + float(r["distance_hi"])) / 2 for r in rest])
y = 100 * np.expm1(np.log(2) * np.array([float(r["log2_ratio_narrow_over_broad"]) for r in rest]))
lo = 100 * np.expm1(np.log(2) * np.array([float(r["ci_low"]) for r in rest]))
hi = 100 * np.expm1(np.log(2) * np.array([float(r["ci_high"]) for r in rest]))
assert np.allclose(y, [100 * (float(r["share_narrow"]) / float(r["share_broad"]) - 1) for r in rest])
ax_a.axhline(0, color=INK, lw=0.6)
ax_a.axhspan(0, 40, color=RED, alpha=0.05, lw=0); ax_a.axhspan(-30, 0, color=BLUE, alpha=0.05, lw=0)
ax_a.fill_between(mid, lo, hi, color=GREY, alpha=0.25, lw=0)
ax_a.plot(mid, y, color=INK, lw=1.0)
ax_a.scatter(mid, y, s=[14 + 26 * (int(r["raw_edges_broad"]) + int(r["raw_edges_narrow"])) /
                        max(int(q["raw_edges_broad"]) + int(q["raw_edges_narrow"]) for q in rest) for r in rest],
             c=[RED if v > 0 else BLUE for v in y], edgecolor="white", lw=0.5, zorder=5)
# same-topic point at x = 0, drawn as a separate marker
ys, sl, sh = [100 * np.expm1(np.log(2) * float(same[k])) for k in ("log2_ratio_narrow_over_broad", "ci_low", "ci_high")]
ax_a.errorbar(0, ys, yerr=[[ys - sl], [sh - ys]], fmt="D", color=RED,
              ms=4.5, capsize=2, lw=0.8, zorder=6, markeredgecolor="white", markeredgewidth=0.5)
ax_a.text(0.004, ys + 2, "same\ntopic", fontsize=5.6, color=RED, ha="left", va="bottom")
ax_a.set_xlim(-0.012, mid.max() * 1.05); ax_a.set_ylim(-25, 38)
from matplotlib.ticker import PercentFormatter
ax_a.yaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))
ax_a.set_xlabel("Title-content distance between the paper's topic and the citing paper's topic\n"
                "(cosine distance; 16 bins from pooled, unweighted distance quantiles)", fontsize=6.2)
ax_a.set_ylabel("Relative difference in citation share (%)\n(narrower-scope versus broader-scope)", fontsize=6.4)
ax_a.text(0.49, 34, "Larger share from\nnearby topics", ha="right", va="top", fontsize=5.8, color=INK)
ax_a.text(0.49, -23, "Smaller share from\nmore distant topics", ha="right", va="bottom", fontsize=5.8, color=INK)
ax_a.spines[["top", "right"]].set_visible(False)
ax_a.set_title("Citation shares shift toward nearby topics", loc="left", fontsize=7.5)
ax_a.tick_params(labelsize=6)

# ---------------------------------------------------------------- b: difference matrix
order = sorted(range(32), key=lambda m: float(next(r for r in nodes if int(r["internal_domain_id"]) == m)["mds_x"]))
M = np.zeros((32, 32))
for r in edges:
    M[int(r["source_internal_domain_id"]), int(r["citing_internal_domain_id"])] = float(r["standardized_share_difference"])
Mo = M[np.ix_(order, order)] * 100
lim = np.percentile(np.abs(Mo), 99)
im = ax_b.imshow(Mo, cmap=CMAP, norm=TwoSlopeNorm(0, -lim, lim), interpolation="nearest", aspect="equal")
ax_b.set_xticks([]); ax_b.set_yticks([])
ax_b.set_xlabel("Citing research area (ordered along the title-content map)", fontsize=6.2)
ax_b.set_ylabel("Paper's research area (same order)", fontsize=6.2)
for spine in ax_b.spines.values():
    spine.set_visible(False)
ax_b.plot([-0.5, 31.5], [-0.5, 31.5], color="none")
cb = fig.colorbar(im, ax=ax_b, fraction=0.045, pad=0.03, extend="both", ticks=[-lim, -lim / 2, 0, lim / 2, lim])
cb.ax.set_yticklabels([f"{v:+.2f}" for v in (-lim, -lim / 2, 0, lim / 2, lim)])
cb.ax.tick_params(labelsize=5.5)
cb.set_label("Standardized share, narrower minus broader (×100)", fontsize=6)
ax_b.set_title("Larger within-area shares, smaller between-area shares", loc="left", fontsize=7.0)

# ---------------------------------------------------------------- c: metrics + LODO
names = {"directed_modularity": ("Within-area concentration\n(directed modularity)", 1),
         "audience_participation": ("Diversity of citing areas\n(participation index)", 1),
         "semantic_span": ("Mean title-content distance\nbetween assigned topic centers", 1)}
ax_c.set_axis_off()
sub = ax_c.get_position()
w = (sub.width - 0.06) / 3
for k, r in enumerate(metrics):
    axk = fig.add_axes([sub.x0 + 0.04 + k * (w + 0.03), sub.y0, w - 0.02, sub.height * 0.62])
    b, n = float(r["broad"]), float(r["specialized"])
    d, dl, dh = float(r["contrast_specialized_minus_broad"]), float(r["ci_low"]), float(r["ci_high"])
    vals = [float(x["contrast_specialized_minus_broad"]) for x in lodo if x["metric"] == r["metric"]]
    axk.axvline(0, color=INK, lw=0.6)
    jitter = np.random.default_rng(3).uniform(-0.18, 0.18, len(vals))
    axk.scatter(vals, 0.55 + jitter, s=7, color=GREY, alpha=0.6, lw=0, zorder=3)
    axk.errorbar(d, 0, xerr=[[d - dl], [dh - d]], fmt="o", color=INK, ms=4.5, capsize=2.5, lw=1.0, zorder=5)
    axk.set_yticks([0, 0.55])
    axk.set_yticklabels(["all areas", "omitting one\narea at a time"] if k == 0 else ["", ""], fontsize=5.6)
    if k:
        axk.tick_params(axis="y", length=0)
    axk.set_ylim(-0.4, 1.0)
    span = max(abs(dl), abs(dh), max(abs(v) for v in vals)) * 1.25
    axk.set_xlim(-span, span)
    axk.set_xlabel("narrower minus broader", fontsize=5.8)
    axk.tick_params(axis="x", labelsize=5.5)
    axk.spines[["top", "right"]].set_visible(False)
    axk.set_title(names[r["metric"]][0], fontsize=6.4, loc="left")
    axk.text(0.02, 0.93, f"{b:.3f} → {n:.3f}", transform=axk.transAxes, fontsize=6, color="#333333", va="top")

fig.text(0.01, 0.965, "a", fontsize=10, fontweight="bold")
fig.text(0.52, 0.965, "b", fontsize=10, fontweight="bold")
fig.text(0.01, sub.y0 + sub.height * 0.95, "c", fontsize=10, fontweight="bold")
fig.text(0.08, sub.y0 + sub.height * 0.95, "Three network summaries point the same way; omitting any one research area does not change them",
         fontsize=7.5, va="center")

for suffix in ("pdf", "png"):
    out = ROOT / "figures" / f"figure4_network.{suffix}"
    fig.savefig(out, dpi=300 if suffix == "png" else None)
    assert out.stat().st_size > 10_000
    print(f"wrote {out.name}: {out.stat().st_size:,} bytes")
n_pos = int((y > 0).sum()); n_neg = int((y < 0).sum())
print(f"validated bins=17 positive_beyond_same_topic={n_pos} negative={n_neg} same_topic={ys:.3f} "
      f"far={y[-3:].round(3).tolist()} concordant_lodo={sum(r['direction_concordant']=='True' for r in lodo)}")
