#!/usr/bin/env python3
"""Figure 4: the same direction in every area, every year, and over ten years.

a, the contrast in each research area and publication year. b, the six publication-year
contrasts, aligned with the heatmap columns. c, the 2015 cohort followed twice as long.
No model is refitted; all values are read from saved source data.
"""
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "source_data"
INK, GREY, RED, FADE = "#222222", "#777777", "#B23A2A", "#9AA6B2"
plt.rcParams.update({"font.family": ["Arial", "Liberation Sans"], "font.size": 6,
                     "pdf.fonttype": 42, "ps.fonttype": 42, "axes.linewidth": 0.6})


def read(name):
    with (DATA / name).open(newline="") as handle:
        return list(csv.DictReader(handle))


areas = sorted(read("SourceData_Figure4_Areas.csv"), key=lambda r: r["display_label"])
years = sorted(read("SourceData_Figure2_Years.csv"), key=lambda r: int(r["level"]))
cells = [r for r in read("SourceData_Figure3_AreaYear.csv") if int(r["qwen_macro"]) != 18]
decomp = read("SourceData_Decomposition.csv")
assert len(areas) == 31 and {r["level"] for r in years} == {str(y) for y in range(2015, 2021)}
assert sum(float(r["estimate"]) < 0 for r in areas) == 27
assert all(float(r["estimate"]) < 0 for r in years)
assert sum(int(r["n"]) for r in years) == 3_827_491
lookup = {(int(r["qwen_macro"]), int(r["publication_year"])): r for r in cells}
assert len(cells) == len(lookup) == 186

matrix = np.full((31, 6), np.nan)
for i, area in enumerate(areas):
    for j, year in enumerate(years):
        row = lookup[int(area["level"]), int(year["level"])]
        assert row["display_label"] == area["display_label"], row
        if row["status"] == "estimated":
            matrix[i, j] = 100 * np.expm1(float(row["estimate"]))
assert np.isfinite(matrix).sum() == 158 and (matrix < 0).sum() == 117
assert np.nanmax(np.abs(matrix)) < 80, "color range must contain every estimate"

fig = plt.figure(figsize=(183 / 25.4, 148 / 25.4))
ax_heat = fig.add_axes([0.245, 0.235, 0.335, 0.680])
ax_year = fig.add_axes([0.245, 0.080, 0.335, 0.105], sharex=ax_heat)
ax_dur = fig.add_axes([0.760, 0.640, 0.200, 0.270])

# ------------------------------------------------------------------- a: area by year ---------
cmap = plt.get_cmap("RdBu").copy()           # red: lower ratio; blue: higher ratio
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
    assert max((luminance + 0.05) / 0.05, 1.05 / (luminance + 0.05)) >= 4.5
    ax_heat.text(j, i, label, ha="center", va="center", fontsize=5.6,
                 color="black" if luminance > 0.179 else "white")
assert marked == [("Orthopaedics & sports medicine", "2019")], marked
for i, j in np.argwhere(np.isnan(matrix)):
    ax_heat.text(j, i, "x", ha="center", va="center", fontsize=5.2, color="#666666")
ax_heat.set(xticks=np.arange(6), xticklabels=[r["level"] for r in years], xlim=(-0.5, 5.5),
            yticks=np.arange(31), yticklabels=[r["display_label"] for r in areas])
ax_heat.tick_params(axis="y", length=0, pad=3, labelsize=5.8)
ax_heat.tick_params(axis="x", top=True, labeltop=True, bottom=False, labelbottom=False,
                    length=0, pad=3, labelsize=6.0)
for spine in ax_heat.spines.values():
    spine.set_visible(False)
ax_heat.set_title("Every research area, every publication year", loc="left", fontsize=7.4, pad=16)

# ------------------------------------------------------------------- b: publication years ----
est, lo, hi = [100 * np.expm1([float(r[k]) for r in years])
               for k in ("estimate", "ci_low", "ci_high")]
positions = np.arange(len(years))
ax_year.axhline(0, color=GREY, lw=0.65)
ax_year.errorbar(positions, est, yerr=[est - lo, hi - est], fmt="o", ms=3.2,
                 color=RED, ecolor=RED, elinewidth=0.8, capsize=2)
ax_year.set(xticks=positions, xticklabels=[r["level"] for r in years],
            ylim=(-22, 12), yticks=[-20, -10, 0, 10])
ax_year.yaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))
ax_year.tick_params(axis="y", length=2, labelsize=5.8)
ax_year.tick_params(axis="x", length=2, labelsize=6.0)
ax_year.set_xlabel("Publication year", fontsize=6.4)
ax_year.spines[["top", "right"]].set_visible(False)
assert np.all(lo > -22) and np.all(hi < 12), "confidence interval clipped"
ax_year.set_title("Pooled over areas", loc="left", fontsize=7.4, pad=6)

# ------------------------------------------------------------------- c: ten-year follow-up ---
WIN = [("theta_y1_5", "Years\n1–5"), ("theta_y6_10", "Years\n6–10")]
for x, (key, label) in enumerate(WIN):
    hits = [r for r in decomp if r["outcome"] == key and r["analysis"] == "ipw_2015"
            and r["scale"] == "log_ratio_of_ratios"]
    assert len(hits) == 1, (key, len(hits))
    r = hits[0]
    e, l, h = [100 * np.expm1(float(r[k])) for k in ("estimate", "ci_low", "ci_high")]
    color = FADE if l < 0 < h else RED
    ax_dur.plot([x, x], [l, h], color=color, lw=1.2)
    for edge in (l, h):
        ax_dur.plot([x - .07, x + .07], [edge, edge], color=color, lw=1.2)
    ax_dur.scatter([x], [e], s=28, color=color, zorder=3)
    ax_dur.text(x + 0.14, e, f"{e:+.1f}%", ha="left", va="center", fontsize=6.2, color=INK)
ax_dur.axhline(0, color=GREY, lw=0.65)
ax_dur.set(xticks=range(len(WIN)), xticklabels=[w[1] for w in WIN], xlim=(-0.55, 1.75))
ax_dur.tick_params(axis="x", length=0, labelsize=6.0, pad=3)
ax_dur.tick_params(axis="y", labelsize=5.8, length=2)
ax_dur.yaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))
ax_dur.spines[["top", "right"]].set_visible(False)
ax_dur.set_title("The 2015 cohort, followed\ntwice as long", loc="left", fontsize=7.4, pad=6)
ax_dur.text(-0.32, -0.30, "596,758 papers from 11,635 journals.\nThe cumulative ten-year ratio minus\n"
                          "the five-year ratio changed by \u22122.0%\n(95% CI, \u22125.3% to +1.4%).",
            transform=ax_dur.transAxes, ha="left", va="top", fontsize=5.8,
            color="#555555", linespacing=1.5)

# ------------------------------------------------------------------- key ----------------------
cax = fig.add_axes([0.690, 0.300, 0.210, 0.013])
bar = fig.colorbar(im, cax=cax, orientation="horizontal", ticks=[-80, -40, 0, 40, 80],
                   format=PercentFormatter(100, decimals=0))
bar.ax.tick_params(labelsize=5.4, length=2, pad=2)
bar.outline.set_linewidth(0.4)
fig.text(0.690, 0.327, "Heatmap: relative difference in the other-area-to-same-topic ratio", fontsize=5.8)
fig.text(0.690, 0.258,
         "Cell labels: rounded percentages.\n"
         "* q < 0.05 (Benjamini\u2013Hochberg).\n"
         "Gray x: fewer than 5,000 papers in a journal\n"
         "group, or fewer than 50 journals.\n\n"
         "Ratio: other-area citations per same-topic\n"
         "citation. Negative values are lower ratios\n"
         "under narrower-scope publication.",
         fontsize=5.6, linespacing=1.55, va="top")
fig.text(0.690, 0.430, "27 of 31 research areas and all six\npublication years had lower\nestimated ratios.",
         fontsize=7.2, linespacing=1.5, color=INK, va="top")

fig.text(0.010, 0.955, "a", fontsize=8, fontweight="bold", va="top")
fig.text(0.010, 0.205, "b", fontsize=8, fontweight="bold", va="top")
fig.text(0.665, 0.955, "c", fontsize=8, fontweight="bold", va="top")

fig.canvas.draw()
assert len(ax_heat.texts) == 186
assert np.allclose(ax_heat.transData.transform([(i, 0) for i in range(6)])[:, 0],
                   ax_year.transData.transform([(i, 0) for i in range(6)])[:, 0]), "columns misaligned"
for suffix in ("pdf", "png"):
    out = ROOT / "figures" / f"figure4_generality.{suffix}"
    fig.savefig(out, dpi=300 if suffix == "png" else None)
    assert out.stat().st_size > 10_000, out
    print(f"wrote {out.name}: {out.stat().st_size:,} bytes")
print("validated 31 areas (27 negative), 6 years (6 negative), 158 numeric labels "
      "(117 negative), 1 BH marker, 28 missing cells; n=3,827,491")
