#!/usr/bin/env python3
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "source_data"
CORAL, BLUE, GREY = "#D55E00", "#0072B2", "#777777"
plt.rcParams.update({"font.family": "Arial", "font.size": 7,
                     "pdf.fonttype": 42, "ps.fonttype": 42,
                     "axes.linewidth": 0.6})

with (DATA / "SourceData_Figure3_AreaYear.csv").open(newline="") as handle:
    cells = list(csv.DictReader(handle))
assert len(cells) == 192, f"expected 192 area-year cells, got {len(cells)}"
estimated = [r for r in cells if r["status"] == "estimated"]
assert len(estimated) == 164, f"expected 164 estimated cells, got {len(estimated)}"
years = list(range(2015, 2021))

# Rows: named research areas with at least one estimable cell, ordered by the
# mean of their cell estimates (most negative first). The Mixed records cluster
# is not a research area and is not displayed.
labels = {}
for r in cells:
    labels.setdefault(int(r["qwen_macro"]), r["display_label"])
named = [r for r in estimated if r["display_label"] != "Mixed records"]
assert len(named) == 158, f"expected 158 named-area cells, got {len(named)}"
means = {}
for r in named:
    means.setdefault(int(r["qwen_macro"]), []).append(float(r["estimate"]))
order = sorted(means, key=lambda m: np.mean(means[m]))
dropped = sorted(labels[m] for m in labels
                 if m not in means and labels[m] != "Mixed records")
assert len(order) == 28 and len(dropped) == 3, (len(order), dropped)

matrix = np.full((len(order), 6), np.nan)
marks = []
for r in named:
    i, j = order.index(int(r["qwen_macro"])), years.index(int(r["publication_year"]))
    matrix[i, j] = float(r["estimate"])
    if float(r["ci_high"]) < 0 or float(r["ci_low"]) > 0:
        marks.append((j, i))

from matplotlib.colors import LinearSegmentedColormap
NAVY, RED, PALE = "#08306B", "#7F0000", "#F7F5F2"
CMAP = LinearSegmentedColormap.from_list("red_navy", [RED, "#C9553D", PALE, "#4A7BB7", NAVY])
POOLED = -0.0824527

fig = plt.figure(figsize=(7.2, 5.0))
ax_heat = fig.add_axes([0.235, 0.20, 0.30, 0.74])
ax_key = fig.add_axes([0.03, 0.03, 0.52, 0.13])
ax_fun = fig.add_axes([0.63, 0.12, 0.355, 0.82])
axes = [ax_heat, ax_fun]

ax = ax_heat
limit = 0.5
cimask = np.zeros_like(matrix, dtype=bool)
for j, i in marks:
    cimask[i, j] = True
image = ax.imshow(np.ma.masked_invalid(matrix), cmap=CMAP, vmin=-limit, vmax=limit,
                  aspect="auto", interpolation="nearest", alpha=0.28)
ax.imshow(np.ma.masked_where(~cimask | np.isnan(matrix), matrix), cmap=CMAP, vmin=-limit,
          vmax=limit, aspect="auto", interpolation="nearest")
for i in range(len(order)):
    for j in range(6):
        if np.isnan(matrix[i, j]):
            ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor="#ECECEC",
                                       edgecolor="none", lw=0))
        elif cimask[i, j]:
            ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor="none",
                                       edgecolor="black", lw=0.8))
ax.set_xticks(range(6)); ax.set_xticklabels(years)
ax.set_yticks(range(len(order))); ax.set_yticklabels([labels[m] for m in order])
ax.tick_params(length=0, pad=2)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.set_title("Negative in 117 of 158 cells; no cell positive", loc="left", fontsize=7.5)

# Key strip under the heatmap: horizontal colour scale with the direction spelled out.
ax_key.set_axis_off()
cax = ax_key.inset_axes([0.36, 0.62, 0.28, 0.16])
bar = fig.colorbar(image, cax=cax, orientation="horizontal", extend="both",
                   ticks=[-0.4, -0.2, 0, 0.2, 0.4])
bar.solids.set_alpha(1)
cax.tick_params(labelsize=5.5, length=2, pad=1)
cax.set_xticklabels(["-0.4", "-0.2", "0", "0.2", "0.4"])
ax_key.text(0.34, 0.62, "Narrower-scope journals receive\nrelatively fewer citations\nfrom other research areas",
            ha="right", va="center", fontsize=5.5, color=RED, transform=ax_key.transAxes)
ax_key.text(0.66, 0.62, "Narrower-scope journals receive\nrelatively more citations\nfrom other research areas",
            ha="left", va="center", fontsize=5.5, color=NAVY, transform=ax_key.transAxes)
ax_key.text(0.50, 0.08, "Log ratio-of-ratios, narrower minus broader. Full color with black outline: 95% CI excludes zero.\n"
            "Faded: 95% CI includes zero. Gray: fewer than 5,000 papers in a journal group or fewer than 50 journals.",
            ha="center", va="bottom", fontsize=5.5, color="#333333", transform=ax_key.transAxes)

# Funnel: estimate against its standard error around the sample-wide contrast.
ax = ax_fun
est = np.array([float(r["estimate"]) for r in named])
se = np.array([float(r["se"]) for r in named])
n = np.array([int(r["n"]) for r in named])
excl = np.array([float(r["ci_high"]) < 0 or float(r["ci_low"]) > 0 for r in named])
size = 6 + 40 * (n - n.min()) / (n.max() - n.min())
grid = np.linspace(0, se.max() * 1.05, 50)
ax.fill_betweenx(grid, POOLED - 1.96 * grid, POOLED + 1.96 * grid, color=NAVY, alpha=0.07, lw=0)
ax.plot(POOLED - 1.96 * grid, grid, color=NAVY, lw=0.7, ls="--")
ax.plot(POOLED + 1.96 * grid, grid, color=NAVY, lw=0.7, ls="--")
ax.axvline(POOLED, color=NAVY, lw=0.9)
ax.axvline(0, color="black", lw=0.6, ls=":")
ax.scatter(est[~excl], se[~excl], s=size[~excl], facecolor="white", edgecolor=GREY, lw=0.6)
ax.scatter(est[excl], se[excl], s=size[excl], color=RED, alpha=0.9, lw=0)
outside = np.abs(est - POOLED) > 1.96 * se
for k in np.argsort(-np.abs(est))[:3]:
    ax.annotate(f"{named[k]['display_label']}, {named[k]['publication_year']}",
                (est[k], se[k]), xytext=(4 if est[k] < 0 else -4, -6),
                textcoords="offset points", ha="left" if est[k] < 0 else "right",
                fontsize=5.5, color="#444444")
ax.set(xlabel="Log ratio-of-ratios in the cell, narrower minus broader",
       ylabel="Standard error of the cell estimate (precise cells at top)",
       xlim=(-0.75, 0.75), ylim=(se.max() * 1.05, 0))
ax.text(POOLED - 0.02, 0.02, "Sample-wide\ncontrast", color=NAVY, ha="right", va="top",
        fontsize=6)
# Legend for marker meaning and size.
from matplotlib.lines import Line2D
handles = [
    Line2D([], [], marker="o", ls="", markerfacecolor=RED, markeredgecolor=RED, ms=5,
           label="95% CI excludes zero"),
    Line2D([], [], marker="o", ls="", markerfacecolor="white", markeredgecolor=GREY, ms=5,
           label="95% CI includes zero"),
]
for count in (10_000, 20_000, 30_000):
    area = 6 + 40 * (count - n.min()) / (n.max() - n.min())
    handles.append(Line2D([], [], marker="o", ls="", markerfacecolor="white",
                          markeredgecolor="#333333", ms=np.sqrt(area),
                          label=f"{count // 1000}k papers in cell"))
ax.legend(handles=handles, loc="upper right", fontsize=5.5, frameon=False,
          handletextpad=0.4, borderaxespad=0.2, labelspacing=0.5, bbox_to_anchor=(1.0, 1.0))
ax.spines[["top", "right"]].set_visible(False)
ax.set_title("Large estimates come from imprecise cells", loc="left", fontsize=7.5)
fig.text(0.02, 0.965, "a", fontsize=10, fontweight="bold")
fig.text(0.565, 0.965, "b", fontsize=10, fontweight="bold")
n_neg = int((est < 0).sum()); n_excl_neg = int((excl & (est < 0)).sum())
n_excl_pos = int((excl & (est > 0)).sum()); n_outside = int(outside.sum())
assert (n_neg, n_excl_neg, n_excl_pos) == (117, 27, 0), (n_neg, n_excl_neg, n_excl_pos)

for suffix in ("pdf", "png"):
    output = ROOT / "figures" / f"figure3_area_year.{suffix}"
    fig.savefig(output, dpi=300 if suffix == "png" else None)
    assert output.stat().st_size > 10_000, f"unexpectedly small output: {output}"
    print(f"wrote {output.name}: {output.stat().st_size:,} bytes")
print(f"validated cells={len(cells)} estimated={len(estimated)} named={len(named)} negative={n_neg} "
      f"excl_neg={n_excl_neg} excl_pos={n_excl_pos} outside_funnel={n_outside}; no estimable cell: {dropped}")
