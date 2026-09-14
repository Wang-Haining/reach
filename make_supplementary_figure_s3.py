#!/usr/bin/env python3
"""Supplementary Figure S3: outcome-blind journal pairs in the eight largest research areas.
a  journal scope scores of the two journals in each pair
b  area-wide contrast (all journals in the area) with 95% CI
"""
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "source_data"
BLUE, RED, INK, GREY = "#2E5C9E", "#B23A2A", "#222222", "#8A8A8A"
plt.rcParams.update({"font.family": ["Arial", "Liberation Sans"], "font.size": 7, "pdf.fonttype": 42,
                     "ps.fonttype": 42, "axes.linewidth": 0.6})

rows = sorted(csv.DictReader((DATA / "SourceData_Figure2_Corridors.csv").open(newline="")),
              key=lambda r: int(r["case_rank"]))
assert len(rows) == 8 and [int(r["case_rank"]) for r in rows] == list(range(1, 9))
assert all(float(r["narrow_scope"]) > float(r["broad_scope"]) for r in rows)

fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(7.2, 4.0), sharey=True, gridspec_kw={"width_ratios": [1, 1], "wspace": 0.18})
y = np.arange(len(rows))[::-1]

# a: scope scores of the two named journals, with names
for k, r in zip(y, rows):
    b, n = float(r["broad_scope"]), float(r["narrow_scope"])
    ax_a.plot([b, n], [k, k], color="#CCCCCC", lw=1.2, zorder=1)
    ax_a.scatter(b, k, color=BLUE, s=22, zorder=3)
    ax_a.scatter(n, k, color=RED, s=22, marker="s", zorder=3)
ax_a.set_yticks(y)
ax_a.set_yticklabels([f"{r['display_label']}\n{r['broad_name']}\nvs {r['narrow_name']}" for r in rows], fontsize=6.2, linespacing=1.1)
for lab in ax_a.get_yticklabels():
    lab.set_ha("right"); lab.set_x(-0.06)
ax_a.set_xlim(0.80, 0.91)
ax_a.set_xlabel("Journal scope score\n(mean title similarity, preceding three years)")
ax_a.spines[["top", "right", "left"]].set_visible(False); ax_a.tick_params(axis="y", length=0)
ax_a.scatter([], [], color=BLUE, s=22, label="Broader-scope journal")
ax_a.scatter([], [], color=RED, s=22, marker="s", label="Narrower-scope journal")
ax_a.legend(frameon=False, loc="upper left", bbox_to_anchor=(0.0, 1.10), fontsize=6.5, ncol=2, handletextpad=0.4, columnspacing=1.2)

# b: area-wide contrast
for k, r in zip(y, rows):
    est, lo, hi = (float(r[c]) for c in ("routing_change_percent", "routing_ci_low_percent", "routing_ci_high_percent"))
    ax_b.plot([lo, hi], [k, k], color=INK, lw=0.9)
    ax_b.scatter(est, k, color=INK, s=18, zorder=3)
    ax_b.text(1.02, k, f"{int(r['area_n']):,}", transform=ax_b.get_yaxis_transform(), ha="left", va="center", fontsize=6, color=GREY)
ax_b.axvline(0, color=INK, lw=0.6, ls=(0, (3, 2)))
ax_b.set_xlim(-32, 40)
ax_b.set_xlabel("Change in the other-area to same-topic citation ratio, %\n(narrower vs broader, all journals in the area)")
ax_b.spines[["top", "right", "left"]].set_visible(False); ax_b.tick_params(axis="y", length=0)
ax_b.text(1.02, len(rows) - 0.4, "papers in area", transform=ax_b.get_yaxis_transform(), ha="left", va="bottom", fontsize=6, color=GREY)

fig.text(0.005, 0.96, "a", fontsize=10, fontweight="bold")
fig.text(0.62, 0.96, "b", fontsize=10, fontweight="bold")
fig.subplots_adjust(left=0.36, right=0.90, bottom=0.21, top=0.90)
for suffix in ("pdf", "png"):
    out = ROOT / "figures" / f"supplementary_figure_s3_journal_pairs.{suffix}"
    fig.savefig(out, dpi=300 if suffix == "png" else None)
    assert out.stat().st_size > 10_000
    print(f"wrote {out.name}: {out.stat().st_size:,} bytes")
