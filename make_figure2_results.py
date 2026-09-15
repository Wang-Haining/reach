#!/usr/bin/env python3
"""Figure 2: papers in narrower-scope journals reached other research areas less.

a, the primary adjusted numbers: citations per paper over five years from other research
   areas, from a different topic in the same area, and from the paper's own topic.
b, the same contrast for every ordered pair of research areas.
c, the contrast estimated separately inside each research area.
Panels run from the finding to its shape to its spread.

Inputs (all under source_data/):
  SourceData_Figure2.csv              a, primary adjusted means
  SourceData_ED3_network_edges.csv    b, standardized flows, 1,024 cells
  SourceData_Hierarchy_Areas.csv      research-area display labels
  SourceData_Figure4_Areas.csv        c, per-area contrasts
"""
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from scipy.cluster.hierarchy import fcluster, leaves_list, linkage
from scipy.spatial.distance import squareform

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "source_data"
BLUE, RED, INK, FADE = "#2E5C9E", "#B23A2A", "#222222", "#9AA6B2"
DIVERGE = LinearSegmentedColormap.from_list(
    "broad_narrow", ["#08306B", "#4A7BB7", "#F7F5F2", "#C9553D", "#7F0000"])
plt.rcParams.update({"font.family": ["Arial", "Liberation Sans"], "font.size": 7,
                     "pdf.fonttype": 42, "ps.fonttype": 42, "axes.linewidth": 0.6})


def read(name):
    with (DATA / name).open(newline="") as handle:
        return list(csv.DictReader(handle))


edges = read("SourceData_ED3_network_edges.csv")
labels = {int(r["qwen_macro"]): r["display_label"] for r in read("SourceData_Hierarchy_Areas.csv")}
labels[18] = "Mixed records"
assert len(edges) == 1024

SHORT = {"Reproduction, metabolism & animal science": "Reproduction & animal science",
         "Clinical diagnostics & case reports": "Clinical diagnostics"}
TIGHT = {"Reproduction, metabolism & animal science": "Reproduction",
         "Clinical diagnostics & case reports": "Clinical diagnostics",
         "Business, economics & policy": "Business & policy",
         "Mathematics & theoretical physics": "Mathematics",
         "Astronomy, optics & imaging": "Astronomy & optics",
         "Orthopaedics & sports medicine": "Orthopaedics",
         "Electronic & magnetic materials": "Electronic materials",
         "Immune & inflammatory disease": "Immune disease",
         "Drug discovery & pharmaceutics": "Drug discovery",
         "Public health & care delivery": "Public health",
         "Marine ecology & paleoscience": "Marine ecology",
         "Electrical & control engineering": "Electrical eng.",
         "Civil & structural engineering": "Civil eng.",
         "Energy & thermal engineering": "Energy eng.",
         "Earth & environmental science": "Earth science",
         "Chronic & infectious disease": "Infectious disease",
         "Climate, land & agriculture": "Climate & agriculture",
         "Electrochemical materials": "Electrochemical",
         "Mental health & cognition": "Mental health",
         "Social behavior & violence": "Social behavior",
         "Education & language": "Education",
         "Cardiovascular medicine": "Cardiovascular",
         "Plant & microbial biology": "Plant & microbial",
         "Cell & neural biology": "Cell & neural",
         "Humanities & politics": "Humanities",
         "Computing & networks": "Computing",
         "Metallurgy & alloys": "Metallurgy",
         "Surgical specialties": "Surgery",
         "Synthetic chemistry": "Synthetic chem.",
         "Ecology & taxonomy": "Ecology",
         "Mixed records": "Mixed records"}

FIG_W, FIG_H = 7.2, 6.4
fig = plt.figure(figsize=(FIG_W, FIG_H))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_axis_off()

LX0, LX1 = 0.022, 0.615          # left column
RX0, RX1 = 0.665, 0.995          # right column


def panel(x, y, letter, title, subtitle=None):
    ax.text(x, y, letter, fontsize=8, fontweight="bold", ha="left", va="top", color=INK, zorder=10)
    ax.text(x + 0.022, y - 0.002, title, fontsize=7.6, fontweight="bold", ha="left", va="top",
            color=INK, zorder=10)
    if subtitle:
        ax.text(x + 0.022, y - 0.021, subtitle, fontsize=6.0, ha="left", va="top",
                color="#555555", zorder=10, linespacing=1.4)


# ============================================================ a: the primary adjusted numbers ==
panel(LX0, 0.992, "a", "Across all 3,818,173 papers in the comparison sample")
prim = {r["outcome"]: r for r in read("SourceData_Figure2.csv")
        if r["analysis"] == "primary" and r["scale"] == "absolute"}
assert round(float(prim["far"]["mean_broad"]), 2) == 2.95
assert round(float(prim["near"]["mean_specialized"]), 2) == 1.96
COLS = [("From other\nresearch areas", "far"), ("Different topic,\nsame area", "intermediate"),
        ("From the\nsame topic", "near")]
AY, CH, VMAX = 0.752, 0.100, 3.1
for k, (lab, key) in enumerate(COLS):
    r = prim[key]
    vb, vn = float(r["mean_broad"]), float(r["mean_specialized"])
    x0 = LX0 + 0.022 + k * 0.128
    for j, (v, col) in enumerate(((vb, BLUE), (vn, RED))):
        ax.add_patch(plt.Rectangle((x0 + j * 0.046, AY), 0.040, CH * v / VMAX, fc=col, ec="none"))
        ax.text(x0 + 0.020 + j * 0.046, AY + CH * v / VMAX + 0.004, f"{v:.2f}",
                ha="center", va="bottom", fontsize=6.2, color=col)
    ax.text(x0 + 0.043, AY - 0.006, lab, ha="center", va="top", fontsize=6.0,
            color="#333333", linespacing=1.35)
    d, lo, hi = float(r["estimate"]), float(r["ci_low"]), float(r["ci_high"])
    ax.text(x0 + 0.043, AY - 0.040, f"{d:+.2f}\n({lo:+.2f}, {hi:+.2f})", ha="center", va="top",
            fontsize=5.6, color=INK if hi < 0 else "#888888", linespacing=1.35)
ax.plot([LX0 + 0.020, LX0 + 0.022 + 2 * 0.128 + 0.088], [AY, AY], color="#333333", lw=0.5)
ax.text(LX0 + 0.020, AY - 0.082,
        "adjusted citations per paper over five years, broader scope then narrower;\n"
        "difference and 95% confidence interval below each pair",
        ha="left", va="top", fontsize=5.6, color="#777777", linespacing=1.45)
ax.text(LX0 + 0.408, AY + 0.078, "9.2% lower", fontsize=13, fontweight="bold", color=RED,
        ha="left", va="center")
ax.text(LX0 + 0.408, AY + 0.030,
        "other-area citations per\nsame-topic citation\n"
        "(1.30 vs 1.44; 95% CI,\n4.8% to 13.4% lower)",
        fontsize=5.9, color="#555555", ha="left", va="center", linespacing=1.5)

# ================================================================= b: area by area ==============
share = {"broad": {}, "narrow": {}}
diff = {}
for r in edges:
    key = (int(r["source_internal_domain_id"]), int(r["citing_internal_domain_id"]))
    share["broad"][key] = float(r["standardized_share_broad"])
    share["narrow"][key] = float(r["standardized_share_specialized"])
    diff[key] = float(r["standardized_share_difference"])
cross = {g: sum(v for (a_, b_), v in share[g].items() if a_ != b_) / sum(share[g].values())
         for g in share}
NAMED = [m for m in range(32) if m != 18]

# Ordered by clustering the pooled citation-flow profiles, not the differences drawn, so the
# diagonal stays the diagonal and related fields sit together.
profile = np.zeros((32, 32))
for r in edges:
    profile[int(r["source_internal_domain_id"]),
            int(r["citing_internal_domain_id"])] = float(r["pooled_standardized_share"])
profile = profile / profile.sum(axis=1, keepdims=True)
link = linkage(squareform(1.0 - np.corrcoef(profile), checks=False), method="average")
leaves = list(leaves_list(link))
assert sorted(leaves) == list(range(32))
# The mixed residual cluster is part of the standardization but is not a research area, so it
# is not displayed; 31 named areas remain, in the clustered order.
row_order = [m for m in leaves if m != 18]
assert len(row_order) == 31

M = np.zeros((32, 32))
for (s_, t_), v in diff.items():
    M[s_, t_] = v
Mo = M[np.ix_(row_order, row_order)] * 100
lim = float(np.percentile(np.abs(Mo), 99))

panel(LX0, 0.632, "b", "Where the citations came from, research area by research area")
MW = 0.444                                       # matrix width in figure fractions
MH = MW * FIG_W / FIG_H
MX0 = LX1 - MW
MY1 = 0.578
MY0 = MY1 - MH
ma = fig.add_axes([MX0, MY0, MW, MH])
im = ma.imshow(Mo, cmap=DIVERGE, vmin=-lim, vmax=lim, interpolation="nearest", aspect="equal")
ma.set_xticks([]); ma.set_yticks([])
for spine in ma.spines.values():
    spine.set_visible(False)
for k, m in enumerate(row_order):
    ma.text(-0.9, k, TIGHT.get(labels[m], labels[m]), ha="right", va="center", fontsize=5.0,
            color="#333333")
    ma.text(k, len(row_order) + 0.1, TIGHT.get(labels[m], labels[m]), ha="right", va="center",
            rotation=55, fontsize=4.7, color="#333333", rotation_mode="anchor")
blocks = fcluster(link, t=5, criterion="maxclust")
for k in [k for k in range(1, len(row_order)) if blocks[row_order[k]] != blocks[row_order[k - 1]]]:
    for draw in ((("#FFFFFF"), 1.4, 2), ("#888888", 0.35, 3)):
        ma.axhline(k - 0.5, color=draw[0], lw=draw[1], zorder=draw[2])
        ma.axvline(k - 0.5, color=draw[0], lw=draw[1], zorder=draw[2])

n_diag_red = sum(1 for m in NAMED if diff[(m, m)] > 0)
n_off_blue = sum(1 for (s_, t_), v in diff.items() if s_ != t_ and 18 not in (s_, t_) and v < 0)
n_off = sum(1 for (s_, t_) in diff if s_ != t_ and 18 not in (s_, t_))
ax.text(LX0 + 0.022, 0.612,
        f"warm diagonal, cool grid: {n_diag_red} of 31 areas kept a larger share of their\n"
        f"citations at home, and {n_off_blue} of the {n_off} between-area cells were smaller",
        fontsize=6.0, color="#555555", ha="left", va="top", linespacing=1.45)

cax = fig.add_axes([LX0 + 0.004, MY0 + MH * 0.30, 0.012, MH * 0.40])
bar = fig.colorbar(im, cax=cax, orientation="vertical", extend="both", ticks=[-lim, 0, lim])
bar.ax.set_yticklabels([f"{-lim:+.2f}", "0", f"{lim:+.2f}"], fontsize=4.6)
bar.ax.tick_params(length=2, pad=1.5)
bar.outline.set_linewidth(0.4)
ax.text(LX0 + 0.010, MY0 + MH * 0.715, "narrower\nscope", ha="center", va="bottom",
        fontsize=5.0, color=RED, linespacing=1.3, zorder=10)
ax.text(LX0 + 0.010, MY0 + MH * 0.285, "broader\nscope", ha="center", va="top",
        fontsize=5.0, color=BLUE, linespacing=1.3, zorder=10)

# ============================================================ c: each area on its own ===========
areas = [r for r in read("SourceData_Figure4_Areas.csv") if r["status"] == "estimated"]
assert len(areas) == 31 and sum(float(r["estimate"]) < 0 for r in areas) == 27
areas = sorted(areas, key=lambda r: float(r["estimate"]))
panel(RX0 - 0.020, 0.992, "c", "Each research area,\non its own")
CY1, CY0 = 0.890, 0.300
CX = RX0 + 0.218
clim = max(abs(float(r[k])) for r in areas for k in ("ci_low", "ci_high"))


def cx(v):
    return CX + 0.104 * v / clim


n_sig = 0
for i, r in enumerate(areas):
    y = CY1 - i * (CY1 - CY0) / (len(areas) - 1)
    est, lo, hi = float(r["estimate"]), float(r["ci_low"]), float(r["ci_high"])
    c = RED if hi < 0 else (FADE if lo < 0 < hi else BLUE)
    n_sig += hi < 0
    ax.plot([cx(lo), cx(hi)], [y, y], color=c, lw=0.9, solid_capstyle="butt", zorder=3)
    ax.scatter([cx(est)], [y], s=9, color=c, lw=0, zorder=4)
    ax.text(CX - 0.117, y, TIGHT.get(r["display_label"], r["display_label"]), ha="right",
            va="center", fontsize=5.2, color="#333333")
ax.plot([cx(0), cx(0)], [CY0 - 0.010, CY1 + 0.008], color=INK, lw=0.5, zorder=2)
AXY = CY0 - 0.016
ax.plot([cx(-clim), cx(clim)], [AXY, AXY], color="#999999", lw=0.5)
for tick in (-0.4, -0.2, 0.0, 0.2, 0.4):
    ax.plot([cx(tick), cx(tick)], [AXY, AXY - 0.005], color="#999999", lw=0.5)
    ax.text(cx(tick), AXY - 0.008, f"{tick:.1f}".replace("-", "\u2212"), ha="center", va="top",
            fontsize=5.2, color="#555555")
ax.text(cx(-clim) - 0.008, AXY - 0.026, "reached less", ha="left", va="top", fontsize=5.2,
        color=RED)
ax.text(cx(clim) + 0.008, AXY - 0.026, "reached more", ha="right", va="top", fontsize=5.2,
        color=BLUE)
ax.text(CX, AXY - 0.046,
        "log ratio of other-area to same-topic citations,\n"
        "narrower minus broader, with 95% CI;\n9 of 31 intervals exclude zero",
        ha="center", va="top", fontsize=5.4, color="#777777", linespacing=1.5)

for suffix in ("pdf", "png"):
    output = ROOT / "figures" / f"figure2_results.{suffix}"
    fig.savefig(output, dpi=300 if suffix == "png" else None)
    assert output.stat().st_size > 10_000, f"unexpectedly small output: {output}"
    print(f"wrote {output.name}: {output.stat().st_size:,} bytes")
print(f"cross broad={cross['broad']:.4f} narrow={cross['narrow']:.4f} diag_red={n_diag_red}/31 "
      f"offdiag_blue={n_off_blue}/{n_off} areas={len(areas)} areas_neg=27 "
      f"areas_ci_excl_zero={n_sig} matrix_rows={len(row_order)}")
