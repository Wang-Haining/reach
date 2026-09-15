#!/usr/bin/env python3
"""Supplementary Figure S6: the same area-by-area difference drawn as a flow graph.

Nodes are the 31 named research areas at their positions on the title-content map of
Supplementary Figure S5. A node's ring is the difference, narrower minus broader, in the share
of its citations that stayed inside the area. Arcs are the between-area flows that together
carry half of all between-area citations, chosen without journal-group labels. Every named
area is labelled. Figure 2a shows the same quantities cell by cell.
"""
import csv
from pathlib import Path

import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MPath

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "source_data"
BLUE, RED, INK = "#2E5C9E", "#B23A2A", "#222222"
plt.rcParams.update({"font.family": ["Arial", "Liberation Sans"], "font.size": 7,
                     "pdf.fonttype": 42, "ps.fonttype": 42, "axes.linewidth": 0.6})


def read(name):
    with (DATA / name).open(newline="") as handle:
        return list(csv.DictReader(handle))


edges = read("SourceData_ED3_network_edges.csv")
labels = {int(r["qwen_macro"]): r["display_label"] for r in read("SourceData_Hierarchy_Areas.csv")}
labels[18] = "Mixed records"
assert len(edges) == 1024

FIG_W, FIG_H = 7.2, 5.0
fig = plt.figure(figsize=(FIG_W, FIG_H))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_axis_off()

pts = np.load(ROOT / "figures" / "cloud_umap_points.npz")
ux, uy, um, us = pts["x"].astype(float), pts["y"].astype(float), pts["macro"].astype(int), pts["status"].astype(int)
assert len(ux) == 1_219_650
x_lo, x_hi = np.percentile(ux, [0.5, 99.5])
y_lo, y_hi = np.percentile(uy, [0.5, 99.5])
keep = (ux > x_lo) & (ux < x_hi) & (uy > y_lo) & (uy < y_hi)
ux, uy, um, us = ux[keep], uy[keep], um[keep], us[keep]
inside = us != 0
area_xy = {m: (float(np.median(ux[(um == m) & inside])), float(np.median(uy[(um == m) & inside])))
           for m in range(32)}

diff, share = {}, {"broad": {}, "narrow": {}}
plot_edge = set()
for r in edges:
    key = (int(r["source_internal_domain_id"]), int(r["citing_internal_domain_id"]))
    diff[key] = float(r["standardized_share_difference"])
    share["broad"][key] = float(r["standardized_share_broad"])
    share["narrow"][key] = float(r["standardized_share_specialized"])
    if r["plot_edge"] == "True":
        plot_edge.add(key)
NAMED = [m for m in range(32) if m != 18]

GX0, GX1, GY0, GY1 = 0.085, 0.915, 0.115, 0.880
def place(m):
    mx, my = area_xy[m]
    return (GX0 + (mx - x_lo) / (x_hi - x_lo) * (GX1 - GX0),
            GY0 + (my - y_lo) / (y_hi - y_lo) * (GY1 - GY0))
node = {m: place(m) for m in range(32)}

backbone = [(s_, t_) for (s_, t_) in plot_edge if s_ != t_ and 18 not in (s_, t_)]
dmax_arc = max(abs(diff[k]) for k in backbone)
for (s_, t_) in sorted(backbone, key=lambda k: abs(diff[k])):
    (xa, ya), (xb, yb) = node[s_], node[t_]
    mx_, my_ = (xa + xb) / 2, (ya + yb) / 2
    dx, dy = xb - xa, yb - ya
    ctrl = (mx_ - dy * 0.18, my_ + dx * 0.18 * (FIG_W / FIG_H))
    path = MPath([(xa, ya), ctrl, (xb, yb)], [MPath.MOVETO, MPath.CURVE3, MPath.CURVE3])
    color = RED if diff[(s_, t_)] > 0 else BLUE
    lw = 0.4 + 3.0 * abs(diff[(s_, t_)]) / dmax_arc
    ax.add_patch(PathPatch(path, fc="none", ec=color, lw=lw * 1.9, alpha=0.16, zorder=4,
                           capstyle="round"))
    ax.add_patch(PathPatch(path, fc="none", ec=color, lw=lw, alpha=0.8, zorder=5,
                           capstyle="round"))

dmax_diag = max(abs(diff[(m, m)]) for m in NAMED)
for m in NAMED:
    x, y = node[m]
    d = diff[(m, m)]
    lw = 0.6 + 3.2 * abs(d) / dmax_diag
    ax.scatter([x], [y], s=70, facecolor="none", edgecolor=RED if d > 0 else BLUE, lw=lw,
               alpha=0.9, zorder=6)
    ax.scatter([x], [y], s=27, facecolor="#8A8A8A", edgecolor="white", lw=0.4, zorder=7)

# Every named area is labelled; labels are nudged vertically until none overlaps another.
SHORT = {"Reproduction, metabolism & animal science": "Reproduction & animal science",
         "Clinical diagnostics & case reports": "Clinical diagnostics"}
pos = {m: np.array([node[m][0], node[m][1] - 0.021]) for m in NAMED}
MINX, MINY = 0.115, 0.0225
for _ in range(600):
    moved = False
    for i, a in enumerate(NAMED):
        for b in NAMED[i + 1:]:
            dx, dy = pos[a] - pos[b]
            if abs(dx) < MINX and abs(dy) < MINY:
                push = (MINY - abs(dy)) / 2 + 1e-4
                sgn = 1.0 if dy >= 0 else -1.0
                pos[a][1] += sgn * push
                pos[b][1] -= sgn * push
                moved = True
    if not moved:
        break
for m in NAMED:
    px_, py_ = pos[m]
    ax.plot([node[m][0], px_], [node[m][1] - 0.008, py_ + 0.006], color="#777777", lw=0.35,
            zorder=8)
    ax.text(px_, py_, SHORT.get(labels[m], labels[m]), fontsize=5.2, ha="center", va="center",
            color="#333333", zorder=9,
            path_effects=[pe.withStroke(linewidth=1.7, foreground="white", alpha=0.95)])

n_ring_red = sum(1 for m in NAMED if diff[(m, m)] > 0)
n_arc_blue = sum(1 for k in backbone if diff[k] < 0)
kx, ky = 0.045, 0.072
ax.scatter([kx], [ky], s=70, facecolor="none", edgecolor=RED, lw=2.0, alpha=0.9, zorder=9)
ax.scatter([kx], [ky], s=27, facecolor="#8A8A8A", edgecolor="white", lw=0.4, zorder=10)
ax.text(kx + 0.022, ky, f"ring: citations staying in the research area;\nred = larger share under "
                        f"narrower scope ({n_ring_red} of 31)",
        ha="left", va="center", fontsize=5.8, color="#444444", linespacing=1.4)
ax.plot([0.500, 0.530], [ky, ky], color=BLUE, lw=2.2, solid_capstyle="round")
ax.text(0.545, ky, f"arc: a flow between two research areas;\nblue = larger share under broader scope "
                   f"({n_arc_blue} of {len(backbone)})",
        ha="left", va="center", fontsize=5.8, color="#444444", linespacing=1.4)
ax.text(0.5, 0.965, "Node positions are the areas' medians on the title-content map "
                    "(Supplementary Figure S5).",
        ha="center", va="top", fontsize=5.8, color="#777777")

for suffix in ("pdf", "png"):
    out = ROOT / "figures" / f"supplementary_figure_s6_network.{suffix}"
    fig.savefig(out, dpi=300 if suffix == "png" else None)
    assert out.stat().st_size > 10_000, out
    print(f"wrote {out.name}: {out.stat().st_size:,} bytes")
print(f"validated rings_red={n_ring_red}/31 arcs={len(backbone)} arcs_blue={n_arc_blue} labels={len(NAMED)}")
