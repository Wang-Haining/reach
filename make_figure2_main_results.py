#!/usr/bin/env python3
"""Figure 2: the same manuscripts, two journal types, two patterns of reach.

Top: paper-level UMAP of a 16% sample of the 7,617,662 eligible two-arm papers
(figures/cloud_umap_points.npz), compared papers coloured by research area.
Middle: the two journal lenses, the counterfactual pair; rain from the same cloud
falls on both. Below: one difference graph of the 31 named research areas
(narrower-scope minus broader-scope standardized citation shares: node rings =
within-area cells, arcs = between-area backbone cells), the per-area bar strip,
the primary AIPW numbers, and one outcome-blind journal pair as an example.

Inputs (all under source_data/ unless noted):
  SourceData_ED3_network_edges.csv   standardized flows, 1,024 cells
  SourceData_Hierarchy_Areas.csv     research-area display labels
  SourceData_Figure2_CloudLeaves.csv leaf-topic counts by comparison status
  SourceData_Figure2_CloudAreas.csv  per-area medians of the display sample
  SourceData_Figure2_Corridors.csv   eight outcome-blind journal corridors
  figures/cloud_umap_points.npz      1,219,650 display points (x, y, area, status)
"""
import colorsys
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_rgba
from matplotlib.patches import PathPatch, Polygon
from matplotlib.path import Path as MPath

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "source_data"
BLUE, RED, INK = "#2E5C9E", "#B23A2A", "#222222"
plt.rcParams.update({"font.family": ["Arial", "Liberation Sans"], "font.size": 7,
                     "pdf.fonttype": 42, "ps.fonttype": 42, "axes.linewidth": 0.6})
rng = np.random.default_rng(20260902)


def read(name):
    with (DATA / name).open(newline="") as handle:
        return list(csv.DictReader(handle))


leaves = read("SourceData_Figure2_CloudLeaves.csv")
edges = read("SourceData_ED3_network_edges.csv")
labels = {int(r["qwen_macro"]): r["display_label"] for r in read("SourceData_Hierarchy_Areas.csv")}
labels[18] = "Mixed records"
assert len(leaves) == 1000 and len(edges) == 1024

lx = np.array([float(r["umap_x"]) for r in leaves])
ly = np.array([float(r["umap_y"]) for r in leaves])
lm = np.array([int(r["qwen_macro"]) for r in leaves])
n_ex = np.array([int(r["n_excluded"]) for r in leaves], float)
n_b = np.array([int(r["n_broad"]) for r in leaves], float)
n_n = np.array([int(r["n_narrow"]) for r in leaves], float)
assert (n_ex.sum(), n_b.sum(), n_n.sum()) == (3_790_171, 1_535_843, 2_291_648)
compared = n_b + n_n
totals = compared + n_ex

FIG_W, FIG_H = 7.0, 8.1
CX0, CX1, CY0, CY1 = 0.04, 0.96, 0.655, 0.985
AREA_COLORS = {m: colorsys.hls_to_rgb(((m * 0.618034) % 1.0), 0.52, 0.50) for m in range(32)}
AREA_COLORS[18] = (0.55, 0.55, 0.55)

fig = plt.figure(figsize=(FIG_W, FIG_H))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_axis_off()

# ---------------------------------------------------------------- cloud ----
# Paper-level UMAP of a 16% proportional sample (1,219,650 papers) of the eligible
# two-arm cohort, embedded on the 32 frozen Qwen3 title components (job 232101).
pts = np.load(ROOT / "figures" / "cloud_umap_points.npz")
ux, uy, um, us = pts["x"].astype(float), pts["y"].astype(float), pts["macro"].astype(int), pts["status"].astype(int)
assert len(ux) == 1_219_650
x_lo, x_hi = np.percentile(ux, [0.5, 99.5]); y_lo, y_hi = np.percentile(uy, [0.5, 99.5])
keep = (ux > x_lo) & (ux < x_hi) & (uy > y_lo) & (uy < y_hi)
ux, uy, um, us = ux[keep], uy[keep], um[keep], us[keep]
cx = CX0 + (ux - x_lo) / (x_hi - x_lo) * (CX1 - CX0)
cy = CY0 + (uy - y_lo) / (y_hi - y_lo) * (CY1 - CY0)
ex = us == 0
ax.scatter(cx[ex], cy[ex], s=0.18, color="#C9C9C9", alpha=0.30, lw=0, zorder=1, rasterized=True)
idx = np.where(~ex)[0]; rng.shuffle(idx)
ax.scatter(cx[idx], cy[idx], s=0.18, c=np.array([AREA_COLORS[k] for k in um[idx]]), alpha=0.42,
           lw=0, zorder=2, rasterized=True)
# Area anchors: medians of compared papers on the display plane.
area_xy = {m: (float(np.median(cx[(um == m) & ~ex])), float(np.median(cy[(um == m) & ~ex]))) for m in range(32)}
compared_area = {m: int(((um == m) & ~ex).sum()) for m in range(32)}
published = {int(r["qwen_macro"]): int(r["n_sampled"]) for r in read("SourceData_Figure2_CloudAreas.csv")}
assert sum(published.values()) == 1_219_650, "published area counts do not sum to the display sample"
# Rain sources: sampled compared papers.
rain_idx = rng.choice(idx, 1200, replace=False)

order = sorted(range(32), key=lambda m: -compared_area[m])
placed = []
for m in order[:16]:
    if m == 18:
        continue
    x, y = area_xy[m]
    for px, py in placed:
        if abs(px - x) < 0.13 and abs(py - y) < 0.028:
            y = py + 0.028 if y >= py else py - 0.028
    placed.append((x, y))
    import matplotlib.patheffects as pe
    dark = tuple(c * 0.55 for c in AREA_COLORS[m])
    ax.text(x, y, labels[m], fontsize=5.2, ha="center", va="center", color=dark, zorder=6,
            fontweight="bold", path_effects=[pe.withStroke(linewidth=1.6, foreground="white", alpha=0.85)])

ax.text(0.008, 0.992, "a", fontsize=10, fontweight="bold", ha="left", va="top", color=INK, zorder=10)
ax.text(0.03, 0.985, "The same manuscripts…", fontsize=9, fontweight="bold", ha="left", va="top", color=INK, zorder=10)
ax.text(0.03, 0.964, "7.62 million eligible articles, 2015–2020, on a title-content map (UMAP of a 16% sample).\n"
        "3.83 million compared papers colored by research area; 3.79 million outside common support in gray.",
        fontsize=5.6, ha="left", va="top", color="#555555", zorder=10)

# ------------------------------------------------------------- journal lenses ----
LENS_Y = 0.585
L = {"broad": (0.05, 0.47), "narrow": (0.53, 0.95)}
COL = {"broad": BLUE, "narrow": RED}


def lens_surface(x, x0, x1, y, kind):
    """Top and bottom y of the lens at horizontal position x."""
    t = np.clip((x - x0) / (x1 - x0), 0, 1)
    bulge = 0.018 * np.sin(np.pi * t)
    if kind == "narrow":
        return y + bulge, y - bulge
    return y + 0.018 - bulge * 0.9, y - 0.018 + bulge * 0.9


def lens(x0, x1, y, kind, color):
    xs = np.linspace(x0, x1, 80)
    top, bot = lens_surface(xs, x0, x1, y, kind)
    poly = np.vstack([np.column_stack([xs, top]), np.column_stack([xs[::-1], bot[::-1]])])
    ax.add_patch(Polygon(poly, closed=True, fc=to_rgba(color, 0.18), ec=color, lw=0.9, zorder=8))


for g, (x0, x1) in L.items():
    lens(x0, x1, LENS_Y, g, COL[g])
ax.text(0.008, LENS_Y + 0.045, "b", fontsize=10, fontweight="bold", ha="left", va="top", color=INK, zorder=10)
ax.text(0.26, LENS_Y + 0.03, "…published in broader-scope journals",
        ha="center", va="bottom", fontsize=7, fontweight="bold", color=BLUE)
ax.text(0.74, LENS_Y + 0.03, "…published in narrower-scope journals",
        ha="center", va="bottom", fontsize=7, fontweight="bold", color=RED)

lens_pos = {}
for g, (x0, x1) in L.items():
    for m in range(32):
        lens_pos[(g, m)] = x0 + 0.02 + (area_xy[m][0] - CX0) / (CX1 - CX0) * (x1 - x0 - 0.04)

for g, half in zip(L, (rain_idx[:600], rain_idx[600:])):
    for i in half:
        x0, y0 = cx[i], cy[i] - 0.01
        x1 = lens_pos[(g, um[i])] + rng.normal(0, 0.004)
        y_top = lens_surface(x1, *L[g], LENS_Y, g)[0]
        path = MPath([(x0, y0), (x0, y0 - 0.03), (x1, y_top + 0.035), (x1, y_top)],
                     [MPath.MOVETO, MPath.CURVE4, MPath.CURVE4, MPath.CURVE4])
        ax.add_patch(PathPatch(path, fc="none", ec=AREA_COLORS[um[i]], lw=0.25, alpha=0.12, zorder=3))

# ------------------------------------------------------------- difference graph ----
share = {"broad": {}, "narrow": {}}
diff, pooled = {}, {}
for r in edges:
    key = (int(r["source_internal_domain_id"]), int(r["citing_internal_domain_id"]))
    share["broad"][key] = float(r["standardized_share_broad"])
    share["narrow"][key] = float(r["standardized_share_specialized"])
    diff[key] = float(r["standardized_share_difference"])
    pooled[key] = float(r["pooled_standardized_share"])
plot_edge = {(int(r["source_internal_domain_id"]), int(r["citing_internal_domain_id"])) for r in edges if r["plot_edge"] == "True"}
cross = {g: sum(v for (a_, b_), v in share[g].items() if a_ != b_) / sum(share[g].values()) for g in share}
row_cross = {g: {s_: 1 - share[g][(s_, s_)] / sum(share[g][(s_, t)] for t in range(32)) for s_ in range(32)} for g in share}
NAMED = [m for m in range(32) if m != 18]

# Node positions: the map, seen obliquely (a parallelogram narrower at the back).
GY0, GY1 = 0.355, 0.528
def oblique(m):
    mx, my = area_xy[m]
    yn = (my - CY0) / (CY1 - CY0)
    xn = (mx - CX0) / (CX1 - CX0)
    depth = 0.62 + 0.38 * (1 - yn)          # back row compressed
    return 0.5 + (xn - 0.5) * 0.92 * depth, GY0 + yn * (GY1 - GY0)
node = {m: oblique(m) for m in range(32)}

# Streams from both lenses to the same communities (thin, uncoloured).
for g in L:
    for m in NAMED:
        x0 = lens_pos[(g, m)]; x1, y1 = node[m]
        y_bot = lens_surface(x0, *L[g], LENS_Y, g)[1]
        path = MPath([(x0, y_bot), (x0, y_bot - 0.03), (x1, y1 + 0.05), (x1, y1)],
                     [MPath.MOVETO, MPath.CURVE4, MPath.CURVE4, MPath.CURVE4])
        ax.add_patch(PathPatch(path, fc="none", ec=to_rgba(COL[g], 0.16), lw=0.35, zorder=3))

# Between-area arcs: backbone cells (>= 50% of between-area citations, chosen without group labels),
# coloured by which journal type carried more of the flow, width by the size of the difference.
backbone = [(s_, t_) for (s_, t_) in plot_edge if s_ != t_ and 18 not in (s_, t_)]
dmax_arc = max(abs(diff[k]) for k in backbone)
for (s_, t_) in sorted(backbone, key=lambda k: abs(diff[k])):
    (xa, ya), (xb, yb) = node[s_], node[t_]
    mx_, my_ = (xa + xb) / 2, (ya + yb) / 2
    dx, dy = xb - xa, yb - ya
    dist = np.hypot(dx, dy)
    ctrl = (mx_ - dy * 0.18, my_ + dx * 0.18 * (FIG_W / FIG_H))
    path = MPath([(xa, ya), ctrl, (xb, yb)], [MPath.MOVETO, MPath.CURVE3, MPath.CURVE3])
    color = RED if diff[(s_, t_)] > 0 else BLUE
    lw = 0.4 + 3.0 * abs(diff[(s_, t_)]) / dmax_arc
    ax.add_patch(PathPatch(path, fc="none", ec=color, lw=lw * 1.9, alpha=0.18, zorder=4, capstyle="round"))
    ax.add_patch(PathPatch(path, fc="none", ec=color, lw=lw, alpha=0.8, zorder=5, capstyle="round"))

# Nodes: dot = research area (cloud colours); ring = within-area cell, red if narrower-scope
# publication kept a larger share of the area's citations inside the area, blue if smaller.
from matplotlib.patches import Wedge, Ellipse
dmax_diag = max(abs(diff[(m, m)]) for m in NAMED)
import matplotlib.patheffects as pe
def ring(x, y, d, size=26):
    """Node dot with a ring whose stroke width encodes |d| (drawn in display space, so it stays round)."""
    lw = 0.6 + 3.2 * abs(d) / dmax_diag
    ax.scatter([x], [y], s=size * 2.6, facecolor="none", edgecolor=RED if d > 0 else BLUE, lw=lw, alpha=0.9, zorder=6)
    ax.scatter([x], [y], s=size, facecolor=(*AREA_COLORS[m], 0.95), edgecolor="white", lw=0.4, zorder=7)


for m in NAMED:
    x, y = node[m]
    ring(x, y, diff[(m, m)])
for m in order[:10]:
    if m == 18:
        continue
    x, y = node[m]
    ax.text(x, y - 0.014, labels[m], fontsize=4.4, ha="center", va="top", color="#333333", zorder=9,
            path_effects=[pe.withStroke(linewidth=1.4, foreground="white", alpha=0.9)])

ax.text(0.008, GY1 + 0.010, "c", fontsize=10, fontweight="bold", ha="left", va="top", color=INK, zorder=10)
ax.text(0.03, GY1 + 0.002, "Where the two journal types sent\nthe same citations differently", ha="left", va="top",
        fontsize=7, fontweight="bold", color=INK, zorder=10, linespacing=1.25,
        path_effects=[pe.withStroke(linewidth=2.5, foreground="white")])
n_ring_red = sum(1 for m in NAMED if diff[(m, m)] > 0)
n_arc_blue = sum(1 for k in backbone if diff[k] < 0)
# compact key, bottom right of the graph
kx, ky = 0.745, GY0 + 0.040
ax.scatter([kx], [ky], s=26 * 2.6, facecolor="none", edgecolor=RED, lw=2.0, alpha=0.9, zorder=9)
ax.scatter([kx], [ky], s=26, facecolor="#999999", edgecolor="white", lw=0.4, zorder=10)
ax.text(kx + 0.018, ky, f"ring: citations staying in the area\nred = more under narrower-scope ({n_ring_red} of 31)",
        ha="left", va="center", fontsize=4.6, color="#444444")
ax.plot([kx - 0.012, kx + 0.012], [ky - 0.026, ky - 0.026], color=BLUE, lw=2.2, solid_capstyle="round")
ax.text(kx + 0.018, ky - 0.026, f"arc: a flow between two areas\nblue = more under broader-scope ({n_arc_blue} of {len(backbone)})",
        ha="left", va="center", fontsize=4.6, color="#444444")
ax.text(0.26, LENS_Y - 0.024, f"{cross['broad']:.0%} of citations came from other research areas", ha="center", va="top",
        fontsize=6.2, fontweight="bold", color=BLUE, zorder=10, path_effects=[pe.withStroke(linewidth=2, foreground="white")])
ax.text(0.74, LENS_Y - 0.024, f"{cross['narrow']:.0%} of citations came from other research areas", ha="center", va="top",
        fontsize=6.2, fontweight="bold", color=RED, zorder=10, path_effects=[pe.withStroke(linewidth=2, foreground="white")])

# ------------------------------------------------------------- bar strip ----
SY = 0.283
ax.text(0.008, SY + 0.036, "d", fontsize=10, fontweight="bold", ha="left", va="top", color=INK, zorder=10)
ax.text(0.5, SY + 0.028, "Area by area: share of citations from other research areas, narrower-scope minus broader-scope journals",
        ha="center", va="bottom", fontsize=5.6, color="#333333")
order_x = sorted(NAMED, key=lambda m: area_xy[m][0])
dmax = max(abs(row_cross["narrow"][m] - row_cross["broad"][m]) for m in NAMED)
XS0, XS1 = 0.15, 0.82
for i, m in enumerate(order_x):
    d = row_cross["narrow"][m] - row_cross["broad"][m]
    x = XS0 + i * ((XS1 - XS0) / (len(order_x) - 1))
    h = 0.024 * d / dmax
    ax.add_patch(plt.Rectangle((x - 0.010, SY), 0.020, h, fc=AREA_COLORS[m], ec="none", alpha=0.95))
ax.plot([XS0 - 0.02, XS1 + 0.02], [SY, SY], color="#333333", lw=0.5)
ax.annotate("", xy=(XS0 - 0.035, SY + 0.024), xytext=(XS0 - 0.035, SY + 0.002),
            arrowprops=dict(arrowstyle="-|>", color=RED, lw=0.7, mutation_scale=6))
ax.annotate("", xy=(XS0 - 0.035, SY - 0.024), xytext=(XS0 - 0.035, SY - 0.002),
            arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=0.7, mutation_scale=6))
ax.text(XS0 - 0.042, SY + 0.013, "narrower-scope\nreached more", ha="right", va="center", fontsize=4.8, color=RED)
ax.text(XS0 - 0.042, SY - 0.013, "broader-scope\nreached more", ha="right", va="center", fontsize=4.8, color=BLUE)
n_lower = sum(1 for m in NAMED if row_cross["narrow"][m] < row_cross["broad"][m])
ax.text(XS1 + 0.03, SY - 0.002, f"{n_lower} of 31 named areas below zero", ha="left", va="top", fontsize=4.8, color="#333333")
ax.text(XS1 + 0.03, SY + 0.002, "bar colour = research area", ha="left", va="bottom", fontsize=4.8, color="#333333")

# ------------------------------------------------------------- bottom band ----
NB_Y = 0.237
ax.text(0.008, NB_Y + 0.010, "e", fontsize=10, fontweight="bold", ha="left", va="top", color=INK, zorder=10)
ax.text(0.03, NB_Y, "Across all 3,818,173 compared papers", fontsize=6.8, fontweight="bold", color=INK, va="top")
ax.text(0.03, NB_Y - 0.020, "From other research areas:  2.95 vs 2.55 citations per paper\n"
        "From the same topic:            2.05 vs 1.96 citations per paper\n"
        "Other-area per same-topic:   1.44 vs 1.30", fontsize=6.2, color="#333333", va="top", linespacing=1.4)
ax.text(0.03, NB_Y - 0.092, "9.2% lower", fontsize=14, fontweight="bold", color=RED, va="top")
ax.text(0.21, NB_Y - 0.094, "for narrower-scope journals\n(95% CI, 4.8% to 13.4% lower)", fontsize=6, color="#555555", va="top")

CASE_RANK = 7   # cardiovascular corridor; rank among the eight outcome-blind corridors
case = next(r for r in read("SourceData_Figure2_Corridors.csv") if int(r["case_rank"]) == CASE_RANK)
SRC = int(case["qwen_macro"])
VX0, VX1, VY0, VY1 = 0.50, 0.975, 0.094, 0.250
sx, sy = area_xy[SRC]
ZR = 0.026
ax.add_patch(Ellipse((sx, sy), 2 * ZR, 2 * ZR * FIG_W / FIG_H, fc="none", ec=INK, lw=0.8, zorder=7))
for px in (VX0, VX1):
    dx, dy = px - sx, VY1 - sy
    d = np.hypot(dx, dy)
    ax.plot([sx + ZR * dx / d, px + (-0.008 if px == VX0 else 0.008)], [sy + ZR * FIG_W / FIG_H * dy / d, VY1], color="#AAAAAA", lw=0.6,
            ls=(0, (3, 2)), zorder=2)
ax.add_patch(plt.Rectangle((VX0 - 0.008, VY0 - 0.004), VX1 - VX0 + 0.016, VY1 - VY0 + 0.004, fc="none", ec="#AAAAAA",
                           lw=0.6, ls=(0, (3, 2)), zorder=2))
ax.text(VX0 - 0.002, VY1 - 0.003, "f", fontsize=10, fontweight="bold", ha="left", va="top", color=INK, zorder=10)
ax.text(VX0 + 0.02, VY1 - 0.010, f"An example: {labels[SRC]}", fontsize=6.4, fontweight="bold", color=INK, va="top")

targets = sorted((t for t in range(32) if t != SRC), key=lambda t: -share["broad"][(SRC, t)])
rmax_share = max(share[g][(SRC, t)] for g in share for t in targets)
n_t = len(targets)
R_IN = 0.30


def rose(rect, g, outline=None):
    ra = fig.add_axes(rect); ra.set_aspect("equal"); ra.set_axis_off()
    ra.set_xlim(-0.80, 0.80); ra.set_ylim(-0.80, 0.80)
    color = COL[g]
    tot = sum(share[g][(SRC, t)] for t in range(32))
    same = share[g][(SRC, SRC)] / tot
    for i, t in enumerate(targets):
        a0 = 90 - i * 360 / n_t; a1 = 90 - (i + 1) * 360 / n_t
        r = R_IN + (0.86 - R_IN) * (share[g][(SRC, t)] / rmax_share) ** 0.25
        ra.add_patch(Wedge((0, 0), r, a1, a0, width=r - R_IN, fc=(*AREA_COLORS[t], 0.92), ec="white", lw=0.3, clip_on=False))
        if outline is not None:
            r0 = R_IN + (0.86 - R_IN) * (share[outline][(SRC, t)] / rmax_share) ** 0.25
            ra.add_patch(Wedge((0, 0), r0, a1, a0, fc="none", ec=COL[outline], lw=0.7, ls=(0, (2, 1.2)), clip_on=False))
    ra.add_patch(plt.Circle((0, 0), R_IN * 0.92, fc="white", ec=color, lw=1.0))
    ra.text(0, 0, f"{same:.0%}\nstay", ha="center", va="center", fontsize=4.8, color=color, fontweight="bold")
    return same


ROSE_H = VY1 - VY0 - 0.004
rw = ROSE_H * FIG_H / FIG_W
stay = {"narrow": rose([VX1 - 0.008 - rw, VY0 - 0.010, rw, ROSE_H], "narrow", outline="broad")}
stay["broad"] = share["broad"][(SRC, SRC)] / sum(share["broad"][(SRC, t)] for t in range(32))
tx = VX0
ax.text(tx, VY1 - 0.030, f"{case['narrow_name']} (narrower-scope, score {float(case['narrow_scope']):.2f})",
        ha="left", va="top", fontsize=5.4, color=RED, fontweight="bold")
ax.text(tx, VY1 - 0.045, f"vs {case['broad_name']} (broader-scope, score {float(case['broad_scope']):.2f})",
        ha="left", va="top", fontsize=5.4, color=BLUE, fontweight="bold")
rb = float(case["far_near_broad"]); rn = float(case["far_near_specialized"])
ax.text(tx, VY1 - 0.068, f"{stay['narrow']:.0%} of citations stayed in the area under narrower-scope\n"
        f"publication, {stay['broad']:.0%} under broader-scope;\n{rn:.2f} vs {rb:.2f} other-area citations per same-topic citation.",
        ha="left", va="top", fontsize=5.4, color=INK, linespacing=1.35)
ax.text(tx, VY1 - 0.112, "Wedges: share of the area's citations from each other\nresearch area under narrower-scope publication;\ndashed outline, the broader-scope value.",
        ha="left", va="top", fontsize=4.6, color="#555555", linespacing=1.3)

# Area colour legend along the bottom: 4 rows x 8 columns.
LEG_Y = 0.076
ax.plot([0.03, 0.97], [LEG_Y + 0.010, LEG_Y + 0.010], color="#DDDDDD", lw=0.5)
leg_order = sorted(range(32), key=lambda m: labels[m])
for i, m in enumerate(leg_order):
    col_i, row_i = i % 4, i // 4
    x = 0.03 + col_i * 0.2375; y = LEG_Y - row_i * 0.0074
    ax.scatter([x], [y], s=8, color=AREA_COLORS[m], lw=0, zorder=9)
    ax.text(x + 0.008, y, labels[m], fontsize=4.2, va="center", color="#333333")

for suffix in ("pdf", "png"):
    output = ROOT / "figures" / f"figure2_main_results.{suffix}"
    fig.savefig(output, dpi=300 if suffix == "png" else None)
    assert output.stat().st_size > 10_000, f"unexpectedly small output: {output}"
    print(f"wrote {output.name}: {output.stat().st_size:,} bytes")
print(f"validated points={len(ux):,} cross_share broad={cross['broad']:.4f} narrow={cross['narrow']:.4f} "
      f"areas_lower={n_lower} rings_red={n_ring_red} arcs={len(backbone)} arcs_blue={n_arc_blue} "
      f"case={labels[SRC]} stay={stay['broad']:.3f}/{stay['narrow']:.3f}")
