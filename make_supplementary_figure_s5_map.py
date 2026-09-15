#!/usr/bin/env python3
"""Supplementary Figure S5: the title-content map, shown for orientation only.

The 1,219,650 display papers placed by title alone, coloured by research area, with the
areas named where they sit. Colour is an atlas, not a scale: every area is named on the
map, so nothing has to be looked up in a legend.

Inputs:
  figures/cloud_umap_points.npz                display points (x, y, macro, status)
  source_data/SourceData_Figure2_CloudAreas.csv per-area medians of the display sample
  source_data/SourceData_Hierarchy_Areas.csv    area display labels
Writes figures/supplementary_figure_s5_map.pdf.
"""
import colorsys
import csv
from pathlib import Path

import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
plt.rcParams.update({"font.family": ["Arial", "Liberation Sans"], "font.size": 7,
                     "pdf.fonttype": 42, "ps.fonttype": 42})

AREA_COLORS = {m: colorsys.hls_to_rgb(((m * 0.618034) % 1.0), 0.50, 0.60) for m in range(32)}
AREA_COLORS[18] = (0.62, 0.62, 0.62)
SHORT = {"Reproduction, metabolism & animal science": "Reproduction &\nanimal science",
         "Clinical diagnostics & case reports": "Clinical\ndiagnostics",
         "Business, economics & policy": "Business, economics\n& policy",
         "Mathematics & theoretical physics": "Mathematics &\ntheoretical physics",
         "Astronomy, optics & imaging": "Astronomy, optics\n& imaging",
         "Orthopaedics & sports medicine": "Orthopaedics &\nsports medicine",
         "Electronic & magnetic materials": "Electronic &\nmagnetic materials",
         "Immune & inflammatory disease": "Immune &\ninflammatory disease",
         "Drug discovery & pharmaceutics": "Drug discovery\n& pharmaceutics",
         "Public health & care delivery": "Public health\n& care delivery",
         "Marine ecology & paleoscience": "Marine ecology\n& paleoscience",
         "Electrical & control engineering": "Electrical & control\nengineering",
         "Civil & structural engineering": "Civil & structural\nengineering",
         "Energy & thermal engineering": "Energy & thermal\nengineering"}


def read(name):
    with (ROOT / "source_data" / name).open(newline="") as handle:
        return list(csv.DictReader(handle))


labels = {int(r["qwen_macro"]): SHORT.get(r["display_label"], r["display_label"])
          for r in read("SourceData_Hierarchy_Areas.csv")}
medians = {int(r["qwen_macro"]): (float(r["umap_x"]), float(r["umap_y"]))
           for r in read("SourceData_Figure2_CloudAreas.csv")}
assert len(labels) == 32 and len(medians) == 32

pts = np.load(ROOT / "figures" / "cloud_umap_points.npz")
x, y, macro = pts["x"], pts["y"], pts["macro"]
N = len(x)
assert N == 1_219_650, N
rng = np.random.default_rng(20260915)
keep = rng.choice(N, 420_000, replace=False)

X0, X1 = np.percentile(x, [1.2, 98.8])
Y0, Y1 = np.percentile(y, [1.2, 98.8])
PAD = 0.075
X0, X1 = X0 - PAD * (X1 - X0), X1 + PAD * (X1 - X0)
Y0, Y1 = Y0 - PAD * (Y1 - Y0), Y1 + PAD * (Y1 - Y0)

MAP_W_IN = 4.8
FIG_W, FIG_H = 7.2, MAP_W_IN * (Y1 - Y0) / (X1 - X0) + 0.18
fig = plt.figure(figsize=(FIG_W, FIG_H))
left = (1 - MAP_W_IN / FIG_W) / 2
ma = fig.add_axes([left, 0.012, MAP_W_IN / FIG_W, 1 - 0.012 - 0.18 / FIG_H])
ma.set_xlim(X0, X1); ma.set_ylim(Y0, Y1); ma.set_axis_off()
ma.scatter(x[keep], y[keep], s=0.20, lw=0,
           c=[AREA_COLORS[m] for m in macro[keep]], alpha=0.42, rasterized=True)

# ---- names where the areas sit; nudged apart, never moved far from the median -------------
order = sorted((m for m in labels if m != 18), key=lambda m: medians[m][1], reverse=True)
pos = {m: np.array(medians[m], dtype=float) for m in order}
sx, sy = (X1 - X0) / MAP_W_IN, (Y1 - Y0) / (FIG_H - 0.18)   # data units per inch
MINX, MINY = 0.98 * sx, 0.155 * sy
for _ in range(400):
    moved = False
    for i, a in enumerate(order):
        for b in order[i + 1:]:
            dx, dy = pos[a] - pos[b]
            if abs(dx) < MINX and abs(dy) < MINY:
                push = (MINY - abs(dy)) / 2 + 1e-3
                s = 1.0 if dy >= 0 else -1.0
                pos[a][1] += s * push
                pos[b][1] -= s * push
                moved = True
    if not moved:
        break
for m in order:
    px_, py_ = pos[m]
    ma.plot([medians[m][0], px_], [medians[m][1], py_], color="#FFFFFF", lw=1.6,
            zorder=4, solid_capstyle="round")
    ma.plot([medians[m][0], px_], [medians[m][1], py_], color="#666666", lw=0.4, zorder=5)
    dark = tuple(0.52 * c for c in AREA_COLORS[m])
    ma.text(px_, py_, labels[m], ha="center", va="center", fontsize=5.0, color=dark,
            linespacing=1.15, zorder=6, clip_on=False,
            path_effects=[pe.withStroke(linewidth=1.9, foreground="white")])

fig.text(0.5, 1 - 0.055 / FIG_H,
         f"{N:,} papers placed by title alone; color and label mark the research area "
         f"each paper's topic belongs to",
         ha="center", va="top", fontsize=6.2, color="#555555")

out = ROOT / "figures" / "supplementary_figure_s5_map.pdf"
fig.savefig(out, dpi=600)
print(f"wrote {out.name}: {out.stat().st_size:,} bytes; {FIG_W:.2f}x{FIG_H:.2f} in; "
      f"labels={len(order)}")
