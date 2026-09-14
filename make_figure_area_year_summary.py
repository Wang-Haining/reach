#!/usr/bin/env python3
"""Display the saved area and year contrasts; no model is refitted."""
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
assert len(areas) == 31 and len({r["level"] for r in areas}) == 31
assert {r["level"] for r in years} == {str(y) for y in range(2015, 2021)}
assert sum(float(r["estimate"]) < 0 for r in areas) == 27
assert all(float(r["estimate"]) < 0 for r in years)
assert all(r["status"] == "estimated" and int(r["journals"]) >= 50 for r in areas + years)
assert sum(int(r["n"]) for r in years) == 3_827_491
fig = plt.figure(figsize=(183 / 25.4, 165 / 25.4))
ax_area = fig.add_axes([0.305, 0.12, 0.37, 0.79])
ax_year = fig.add_axes([0.785, 0.57, 0.20, 0.34])
for ax, rows, key in ((ax_area, areas, "display_label"), (ax_year, years, "level")):
    est, lo, hi = [100 * np.expm1([float(r[k]) for r in rows]) for k in ("estimate", "ci_low", "ci_high")]
    assert np.isfinite([est, lo, hi]).all() and np.all(lo <= est) and np.all(est <= hi)
    positions = np.arange(len(rows))
    for y in positions[::2]:
        ax.axhspan(y - 0.5, y + 0.5, color="#F4F4F4", lw=0, zorder=0)
    ax.axvline(0, color=GREY, lw=0.65, zorder=1)
    ax.errorbar(est, positions, xerr=[est - lo, hi - est], fmt="o", ms=3.2,
                color=INK, ecolor=GREY, elinewidth=0.65, capsize=1.8, zorder=3)
    ax.set(yticks=positions, yticklabels=[r[key] for r in rows],
           ylim=(len(rows) - 0.5, -0.5), xlim=(-50, 65), xticks=[-40, -20, 0, 20, 40, 60])
    ax.xaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))
    ax.tick_params(axis="y", length=0, pad=4, labelsize=5.6 if key == "display_label" else 6.5)
    ax.tick_params(axis="x", length=2, labelsize=5.5)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.set_xlabel("Relative difference in other-area / same-topic citation ratio", fontsize=5.7)
ax_year.set_xlabel("Relative difference in citation ratio", fontsize=5.7)
ax_area.set_title("Across research areas", loc="left", fontsize=7, pad=9)
ax_year.set_title("Across publication years", loc="left", fontsize=7, pad=9)
fig.text(0.025, 0.94, "a", fontsize=8, fontweight="bold")
fig.text(0.73, 0.94, "b", fontsize=8, fontweight="bold")
fig.text(0.77, 0.45, "27 of 31 areas\n6 of 6 years", fontsize=11, color=INK, linespacing=1.5)
fig.text(0.77, 0.36, "had a lower estimated\nother-area / same-topic\ncitation ratio in\nnarrower-scope journals.", fontsize=7, linespacing=1.4)
fig.text(0.77, 0.235, "Points: adjusted contrasts\nLines: 95% confidence intervals\nAll estimates are shown.", fontsize=6, color=GREY, linespacing=1.5)
fig.text(0.305, 0.045, "Negative: lower ratio in narrower-scope journals     Positive: higher ratio", fontsize=6)
fig.text(0.305, 0.021, "All panels use the regenerated comparison sample; shared percentage scale.", fontsize=5.8, color=GREY)
for suffix in ("pdf", "png"):
    out = ROOT / "figures" / f"figure3_area_year.{suffix}"
    fig.savefig(out, dpi=300 if suffix == "png" else None)
    assert out.stat().st_size > 10_000, out
    print(f"wrote {out.name}: {out.stat().st_size:,} bytes")
print("validated 31 areas (27 negative), 6 years (6 negative), n=3,827,491; saved estimates unchanged")
