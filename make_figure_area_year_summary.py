#!/usr/bin/env python3
"""Align saved area, area-year, and year contrasts; no model is refitted."""
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter

ROOT = Path(__file__).resolve().parent
INK, GREY = "#222222", "#777777"
plt.rcParams.update({"font.family": "Arial", "font.size": 6,
                     "pdf.fonttype": 42, "ps.fonttype": 42, "axes.linewidth": 0.6})
with (ROOT / "source_data/SourceData_Figure4_Areas.csv").open() as f:
    areas = sorted(csv.DictReader(f), key=lambda r: r["display_label"])
with (ROOT / "source_data/SourceData_Figure2_Years.csv").open() as f:
    years = sorted(csv.DictReader(f), key=lambda r: int(r["level"]))
with (ROOT / "source_data/SourceData_Figure3_AreaYear.csv").open() as f:
    cells = [r for r in csv.DictReader(f) if int(r["qwen_macro"]) != 18]
assert len(areas) == 31 and len({r["level"] for r in areas}) == 31
assert {r["level"] for r in years} == {str(y) for y in range(2015, 2021)}
assert sum(float(r["estimate"]) < 0 for r in areas) == 27
assert all(float(r["estimate"]) < 0 for r in years)
assert all(r["status"] == "estimated" and int(r["journals"]) >= 50 for r in areas + years)
assert sum(int(r["n"]) for r in years) == 3_827_491
lookup = {(int(r["qwen_macro"]), int(r["publication_year"])): r for r in cells}
assert len(cells) == len(lookup) == 186, f"expected 186 unique area-year cells, got {len(cells)}, {len(lookup)}"
matrix = np.full((31, 6), np.nan)
for i, area in enumerate(areas):
    for j, year in enumerate(years):
        row = lookup[int(area["level"]), int(year["level"])]
        assert row["display_label"] == area["display_label"], row
        assert row["status"] in {"estimated", "not_estimable"}, row
        if row["status"] == "estimated":
            matrix[i, j] = 100 * np.expm1(float(row["estimate"]))
assert np.isfinite(matrix).sum() == 158 and np.isnan(matrix).sum() == 28
assert (matrix < 0).sum() == 117 and np.isnan(matrix).all(axis=1).sum() == 3
assert np.nanmax(np.abs(matrix)) < 80, "color range must contain every estimate"
fig = plt.figure(figsize=(183 / 25.4, 165 / 25.4))
ax_area = fig.add_axes([0.30, 0.285, 0.27, 0.64])
ax_heat = fig.add_axes([0.625, 0.285, 0.36, 0.64], sharey=ax_area)
ax_year = fig.add_axes([0.625, 0.10, 0.36, 0.115], sharex=ax_heat)
for ax, rows in ((ax_area, areas), (ax_year, years)):
    est, lo, hi = [100 * np.expm1([float(r[k]) for r in rows]) for k in ("estimate", "ci_low", "ci_high")]
    assert np.isfinite([est, lo, hi]).all() and np.all(lo <= est) and np.all(est <= hi)
    positions = np.arange(len(rows))
    if ax is ax_area:
        for y in positions[::2]:
            ax.axhspan(y - 0.5, y + 0.5, color="#F4F4F4", lw=0, zorder=0)
        ax.axvline(0, color=GREY, lw=0.65)
        ax.errorbar(est, positions, xerr=[est - lo, hi - est], fmt="o", ms=3,
                    color=INK, ecolor=GREY, elinewidth=0.65, capsize=1.8)
        ax.set(yticks=positions, yticklabels=[r["display_label"] for r in rows],
               ylim=(30.5, -0.5), xlim=(-50, 65), xticks=[-40, -20, 0, 20, 40, 60])
        ax.xaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))
        ax.tick_params(axis="y", length=0, pad=4, labelsize=5.4)
        ax.set_xlabel("Relative difference in citation ratio", fontsize=6)
    else:
        ax.axhline(0, color=GREY, lw=0.65)
        ax.errorbar(positions, est, yerr=[est - lo, hi - est], fmt="o", ms=3,
                    color=INK, ecolor=GREY, elinewidth=0.65, capsize=2)
        ax.set(xticks=positions, xticklabels=[r["level"] for r in rows],
               ylim=(-22, 12), yticks=[-20, -10, 0, 10])
        ax.yaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))
        ax.tick_params(axis="y", length=2, labelsize=5.5)
        ax.set_xlabel("Publication year", fontsize=6)
    ax.tick_params(axis="x", length=2, labelsize=5.5)
    ax.spines[["top", "right"]].set_visible(False)
    lower, upper = ax.get_xlim() if ax is ax_area else ax.get_ylim()
    assert np.all(lo > lower) and np.all(hi < upper), f"confidence interval clipped: {lo.min()}, {hi.max()} outside {lower}, {upper}"
ax_area.spines["left"].set_visible(False)
cmap = plt.get_cmap("RdBu").copy()  # Red: lower ratio; blue: higher ratio.
cmap.set_bad("#D9D9D9")
im = ax_heat.imshow(np.ma.masked_invalid(matrix), cmap=cmap, vmin=-80, vmax=80,
                    aspect="auto", interpolation="nearest")
marked = []
for i, j in np.argwhere(np.isfinite(matrix)):
    row = lookup[int(areas[i]["level"]), int(years[j]["level"])]
    q = float(row["q_value_bh"])
    assert np.isfinite(q) and 0 <= q <= 1, row
    value = round(matrix[i, j])
    label = f"{value:+d}" if value else "0"
    if q < 0.05:
        label += "*"
        marked.append((row["display_label"], row["publication_year"]))
    rgb = np.array(cmap(im.norm(matrix[i, j]))[:3])
    linear = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    luminance = linear @ [0.2126, 0.7152, 0.0722]
    color = "black" if luminance > 0.179 else "white"
    assert max((luminance + 0.05) / 0.05, 1.05 / (luminance + 0.05)) >= 4.5
    ax_heat.text(j, i, label, ha="center", va="center", fontsize=5.4, color=color)
assert marked == [("Orthopaedics & sports medicine", "2019")], marked
for i, j in np.argwhere(np.isnan(matrix)):
    ax_heat.text(j, i, "x", ha="center", va="center", fontsize=5, color="#666666")
ax_heat.set(xticks=np.arange(6), xticklabels=[r["level"] for r in years], xlim=(-0.5, 5.5))
ax_heat.tick_params(axis="y", left=False, labelleft=False)
ax_heat.tick_params(axis="x", top=True, labeltop=True, bottom=False, labelbottom=False, length=0, pad=3, labelsize=5.5)
for spine in ax_heat.spines.values():
    spine.set_visible(False)
ax_area.set_title("Across research areas", loc="left", fontsize=7, pad=17)
ax_heat.set_title("Within each area, year by year", loc="left", fontsize=7, pad=17)
ax_year.set_title("Across publication years", loc="left", fontsize=7, pad=7)
cax = fig.add_axes([0.315, 0.195, 0.235, 0.014])
bar = fig.colorbar(im, cax=cax, orientation="horizontal", ticks=[-80, -40, 0, 40, 80], format=PercentFormatter(100, decimals=0))
bar.ax.tick_params(labelsize=5, length=2, pad=2)
bar.outline.set_linewidth(0.4)
fig.text(0.30, 0.225, "Heatmap: relative difference in citation ratio", fontsize=5.6)
fig.text(0.30, 0.14, "Cell labels: rounded percentages\n* q < 0.05 (BH-adjusted); gray x: not estimated", fontsize=5.4, linespacing=1.4)
fig.text(0.30, 0.095, "27 of 31 areas and all six years\nhad lower estimated ratios.", fontsize=7, linespacing=1.45)
fig.text(0.265, 0.958, "a", fontsize=8, fontweight="bold")
fig.text(0.59, 0.958, "b", fontsize=8, fontweight="bold")
fig.text(0.59, 0.237, "c", fontsize=8, fontweight="bold")
fig.text(0.30, 0.028, "Ratio: other-area / same-topic citations. Negative values: lower in narrower-scope journals.", fontsize=5.6)
fig.canvas.draw()
assert len(ax_heat.texts) == 186
for label in ax_heat.texts:
    box = label.get_window_extent(fig.canvas.get_renderer())
    assert box.width < ax_heat.bbox.width / 6 and box.height < ax_heat.bbox.height / 31
assert np.allclose(ax_area.transData.transform([(0, i) for i in range(31)])[:, 1],
                   ax_heat.transData.transform([(0, i) for i in range(31)])[:, 1]), "area rows are not aligned"
assert np.allclose(ax_heat.transData.transform([(i, 0) for i in range(6)])[:, 0],
                   ax_year.transData.transform([(i, 0) for i in range(6)])[:, 0]), "year columns are not aligned"
for suffix in ("pdf", "png"):
    out = ROOT / "figures" / f"figure3_area_year.{suffix}"
    fig.savefig(out, dpi=300 if suffix == "png" else None)
    assert out.stat().st_size > 10_000, out
    print(f"wrote {out.name}: {out.stat().st_size:,} bytes")
print("validated aligned 31 areas (27 negative), 6 years (6 negative), 158 numeric labels (117 negative estimates), 1 existing BH marker, 28 missing cells; n=3,827,491; saved estimates unchanged")
