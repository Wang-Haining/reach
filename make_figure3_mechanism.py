#!/usr/bin/env python3
"""Figure 3: where the shortfall in reach sits.

a, three measures of use outside the paper's own research area.
b, the identity that splits the other-area citation count into entry and intensity.
c, citation-share differences across title-content distances.
d, three whole-graph summaries of concentration, each as an absolute difference, with the
   32 leave-one-area-out estimates behind them.

Inputs (all under source_data/):
  SourceData_Decomposition.csv              a, b
  SourceData_Figure4_DistanceEnrichment.csv c
  SourceData_Figure3_metrics.csv            d
  SourceData_ED3_lodo.csv                   d
"""
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "source_data"
BLUE, RED, INK, GREY = "#2E5C9E", "#B23A2A", "#222222", "#8A8A8A"
FADE = "#9AA6B2"
plt.rcParams.update({"font.family": ["Arial", "Liberation Sans"], "font.size": 7,
                     "pdf.fonttype": 42, "ps.fonttype": 42, "axes.linewidth": 0.6})


def read(name):
    with (DATA / name).open(newline="") as handle:
        return list(csv.DictReader(handle))


rows = read("SourceData_Decomposition.csv")
enrich = read("SourceData_Figure4_DistanceEnrichment.csv")
metrics = read("SourceData_Figure3_metrics.csv")
lodo = read("SourceData_ED3_lodo.csv")
assert len(enrich) == 17 and len(metrics) == 3 and len(lodo) == 96


def get(outcome, analysis="aipw", scale="log_mean_ratio"):
    hits = [r for r in rows if r["outcome"] == outcome
            and r["analysis"] == analysis and r["scale"] == scale]
    if len(hits) != 1:
        raise SystemExit(f"expected one row for {(analysis, outcome, scale)}, found {len(hits)}")
    return hits[0]


def num(r, key):
    if r[key] in ("", None):
        raise SystemExit(f"row {r['outcome']!r} is missing {key}")
    return float(r[key])


def pct(x):
    return (np.exp(x) - 1.0) * 100.0


FIG_W, FIG_H = 7.2, 4.85
fig = plt.figure(figsize=(FIG_W, FIG_H))
gs = fig.add_gridspec(2, 2, width_ratios=[1.28, 0.86], height_ratios=[1.0, 1.06],
                      wspace=0.42, hspace=0.62, left=0.155, right=0.975,
                      bottom=0.085, top=0.905)

# ------------------------------------------------------------------ a: the three measures ----
ax = fig.add_subplot(gs[0, 0])
LADDER = [("any_far_all32", "Reached by any other\nresearch area at all"),
          ("n_macros_other_named31", "Number of other research\nareas reached"),
          ("far_all32", "Citations from other\nresearch areas")]
ys = np.arange(len(LADDER))[::-1]
for y, (key, label) in zip(ys, LADDER):
    r = get(key)
    est, lo, hi = pct(num(r, "estimate")), pct(num(r, "ci_low")), pct(num(r, "ci_high"))
    color = FADE if lo < 0 < hi else RED
    ax.plot([lo, hi], [y, y], color=color, lw=1.2, solid_capstyle="butt", zorder=2)
    for edge in (lo, hi):
        ax.plot([edge, edge], [y - .10, y + .10], color=color, lw=1.2, zorder=2)
    ax.scatter([est], [y], s=28, color=color, zorder=3, clip_on=False)
    ax.text(est, y + 0.26, f"{est:+.1f}%", ha="center", va="bottom", fontsize=6.4, color=INK)
ax.axvline(0, color=INK, lw=0.6, zorder=1)
ax.set_yticks(ys)
ax.set_yticklabels([lab for _, lab in LADDER], fontsize=6.4, linespacing=1.25)
ax.set_ylim(-0.6, len(LADDER) - 0.3)
ax.set_xlabel("Difference under narrower-scope publication (%)", fontsize=6.4)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(axis="y", length=0)
ax.tick_params(axis="x", labelsize=6)
ax.set_title("Other research areas still arrived; they drew less", loc="left", fontsize=7.4, pad=8)

# ------------------------------------------------------------------ b: the identity ----------
ax = fig.add_subplot(gs[0, 1])
tot = num(get("decomp_total"), "estimate")
ent = num(get("decomp_entry"), "estimate")
inten = num(get("decomp_intensity"), "estimate")
if abs(tot - (ent + inten)) > 5e-4:
    raise SystemExit(f"identity fails: {tot} != {ent} + {inten}")
bars = [("Citations from other\nresearch areas", tot, RED),
        ("Whether any\narrived", ent, FADE),
        ("How many\nthey sent", inten, RED)]
for x, (label, val, color) in enumerate(bars):
    v = pct(val)
    ax.bar(x, v, width=0.58, color=color, edgecolor="none")
    if v < -6:
        ax.text(x, v + 1.2, f"{v:+.1f}%", ha="center", va="bottom", fontsize=6.4, color="white")
    else:
        ax.text(x, 0.7, f"{v:+.1f}%", ha="center", va="bottom", fontsize=6.4, color=INK)
ax.axhline(0, color=INK, lw=0.6)
ax.set_xticks(range(3))
ax.set_xticklabels([b[0] for b in bars], fontsize=6.2, linespacing=1.25)
ax.set_ylabel("Difference (%)", fontsize=6.4)
ax.set_ylim(min(pct(tot), pct(inten)) * 1.20, 4.6)
ax.tick_params(labelsize=6)
ax.spines[["top", "right"]].set_visible(False)
ax.set_title("Entry and intensity account for the shortfall", loc="left", fontsize=7.4, pad=8)
c = get("decomp_contrast", scale="log_ratio_contrast")
ax.text(0.5, 0.035, f"intensity versus entry  {pct(num(c,'estimate')):+.1f}%"
                    f"  ({pct(num(c,'ci_low')):+.0f}%, {pct(num(c,'ci_high')):+.0f}%)",
        transform=ax.transAxes, ha="center", va="bottom", fontsize=5.9, color="#555555")

# ------------------------------------------------------------------ c: distance gradient -----
ax = fig.add_subplot(gs[1, 0])
same, rest = enrich[0], enrich[1:]
mid = np.array([(float(r["distance_lo"]) + float(r["distance_hi"])) / 2 for r in rest])
y = 100 * np.expm1(np.log(2) * np.array([float(r["log2_ratio_narrow_over_broad"]) for r in rest]))
lo = 100 * np.expm1(np.log(2) * np.array([float(r["ci_low"]) for r in rest]))
hi = 100 * np.expm1(np.log(2) * np.array([float(r["ci_high"]) for r in rest]))
assert np.allclose(y, [100 * (float(r["share_narrow"]) / float(r["share_broad"]) - 1) for r in rest])
ax.axhline(0, color=INK, lw=0.6)
ax.fill_between(mid, lo, hi, color=GREY, alpha=0.22, lw=0)
ax.plot(mid, y, color=INK, lw=1.0)
weight = np.array([int(r["raw_edges_broad"]) + int(r["raw_edges_narrow"]) for r in rest], dtype=float)
ax.scatter(mid, y, s=14 + 26 * weight / weight.max(),
           c=[RED if v > 0 else BLUE for v in y], edgecolor="white", lw=0.5, zorder=5)
ys_, sl, sh = [100 * np.expm1(np.log(2) * float(same[k]))
               for k in ("log2_ratio_narrow_over_broad", "ci_low", "ci_high")]
ax.errorbar(0, ys_, yerr=[[ys_ - sl], [sh - ys_]], fmt="D", color=RED, ms=4.5, capsize=2,
            lw=0.9, zorder=6, markeredgecolor="white", markeredgewidth=0.5)
ax.text(0.006, ys_ + 1.5, "the paper's\nown topic", fontsize=5.9, color=RED, ha="left", va="bottom")
ax.set_xlim(-0.014, mid.max() * 1.05)
ax.set_ylim(-25, 38)
ax.yaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))
ax.set_xlabel("Title-content distance from the paper's topic to the citing paper's topic\n"
              "(cosine distance; 16 bins of pooled, unweighted citation distances)", fontsize=6.2)
ax.set_ylabel("Relative difference in citation share\nnarrower versus broader scope (%)", fontsize=6.4)
ax.text(0.485, 35, "larger share from nearby topics", ha="right", va="top", fontsize=6.0, color=RED)
ax.text(0.485, -23, "smaller share from distant topics", ha="right", va="bottom", fontsize=6.0, color=BLUE)
ax.tick_params(labelsize=6)
ax.spines[["top", "right"]].set_visible(False)
ax.set_title("Nearby shares were higher, distant shares lower", loc="left", fontsize=7.4, pad=8)

# ------------------------------------------------------------------ d: whole-graph summaries --
ax = fig.add_subplot(gs[1, 1])
NAMES = {"directed_modularity": "Concentration within\nthe research area",
         "audience_participation": "Diversity of citing\nresearch areas",
         "semantic_span": "Title-content distance\ncited to citing"}
positions = np.arange(len(metrics))[::-1]
for pos, r in zip(positions, metrics):
    d = float(r["contrast_specialized_minus_broad"])
    dl, dh = float(r["ci_low"]), float(r["ci_high"])
    vals = [float(x["contrast_specialized_minus_broad"])
            for x in lodo if x["metric"] == r["metric"]]
    # A strip of the 32 leave-one-area-out estimates: one tick each, no jitter.
    lane = pos + 0.30
    ax.plot([min(vals), max(vals)], [lane, lane], color=GREY, lw=0.4, alpha=0.5, zorder=1)
    for v in vals:
        ax.plot([v, v], [lane - 0.095, lane + 0.095], color=GREY, lw=0.4, alpha=0.8,
                solid_capstyle="butt", zorder=2)
    ax.plot([dl, dh], [pos, pos], color=RED, lw=1.2, solid_capstyle="butt", zorder=3)
    for edge in (dl, dh):
        ax.plot([edge, edge], [pos - .09, pos + .09], color=RED, lw=1.2, zorder=3)
    ax.scatter([d], [pos], s=28, color=RED, zorder=4)
    ax.text(d, pos - 0.30, f"{d:+.3f}", ha="center", va="top", fontsize=6.2, color=INK)
ax.axvline(0, color=INK, lw=0.6, zorder=1)
ax.set_yticks(positions)
ax.set_yticklabels(list(NAMES.values()), fontsize=6.2, linespacing=1.25)
ax.set_ylim(-0.55, len(metrics) - 0.25)
ax.set_xlim(-0.055, 0.055)
ax.set_xticks([-0.04, -0.02, 0, 0.02, 0.04])
ax.set_xlabel("Difference in graph metric\nnarrower minus broader scope", fontsize=6.4)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(axis="y", length=0)
ax.tick_params(axis="x", labelsize=6)
ax.set_title("The whole citation graph was more local", loc="left", fontsize=7.4, pad=8)
ax.text(0.5, -0.40, "gray ticks: each estimate omits one research area",
        transform=ax.transAxes, ha="center", va="top", fontsize=5.8, color=GREY)

for x, ypos, lab in ((0.006, 0.975, "a"), (0.595, 0.975, "b"),
                     (0.006, 0.487, "c"), (0.595, 0.487, "d")):
    fig.text(x, ypos, lab, fontsize=8, fontweight="bold", va="top")

for suffix in ("pdf", "png"):
    out = ROOT / "figures" / f"figure3_mechanism.{suffix}"
    fig.savefig(out, dpi=300 if suffix == "png" else None)
    assert out.stat().st_size > 10_000, out
    print(f"wrote {out.name}: {out.stat().st_size:,} bytes")
print(f"validated bins=17 near_positive={(y > 0).sum()} far_negative={(y < 0).sum()} "
      f"same_topic={ys_:.1f}% lodo={len(lodo)} concordant="
      f"{sum(r['direction_concordant'] == 'True' for r in lodo)}")
