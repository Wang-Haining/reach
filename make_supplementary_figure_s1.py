#!/usr/bin/env python3
"""Supplementary Figure S1: sample construction (STROBE-style flow).

Writes the diagram twice from one geometry: a draw.io file (figures/…s1….drawio) that can be
edited by hand, and the PDF/PNG that the supplement includes. Counts are asserted against
SourceData_ED1_cohort_coverage.csv and the sample-lineage table in CLAUDE_PROVENANCE.md.
"""
import csv
import html
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parent
FILL, FRAME, INK = "#DAE8FC", "#7F7F7F", "#222222"
plt.rcParams.update({"font.family": ["Arial", "Liberation Sans"], "pdf.fonttype": 42, "ps.fonttype": 42})

BASE, SCORED, EXTREME, ELIGIBLE, PRIMARY = 19_896_656, 15_233_734, 7_683_322, 7_617_662, 3_818_173
ELIG_BROAD, ELIG_NARROW, PRIMARY_JOURNALS = 3_268_625, 4_349_037, 20_203
REGEN, REGEN_BROAD, REGEN_NARROW, REGEN_JOURNALS = 3_827_491, 1_535_843, 2_291_648, 20_215
assert ELIG_BROAD + ELIG_NARROW == ELIGIBLE and REGEN_BROAD + REGEN_NARROW == REGEN
cov = {(r["panel"], r["measure"]): float(r["value"])
       for r in csv.DictReader((ROOT / "source_data" / "SourceData_ED1_cohort_coverage.csv").open())}
assert cov[("a", "Eligible focal papers")] == ELIGIBLE and cov[("a", "Subgroup and network sample")] == REGEN
EXCL_SJ, UNCLASS, INCLUDED = (int(cov[("d", k)]) for k in ("Same journal/author", "Area unavailable", "Included"))
ALL_EDGES = EXCL_SJ + UNCLASS + INCLUDED
f = "{:,}".format

# ---- geometry (draw.io pixels; 1 px = 1 pt in the PDF) ------------------------------------
MW, MH, SW = 340, 58, 260           # main box width/height; side box width (same height)
MX, SX, GAP, TOP = 40, 440, 36, 30
main = [
    ("Original journal articles in OpenAlex, 2015–2020", f"{f(BASE)} papers",
     "With a title and a publishing journal; reviews, retractions, and duplicates excluded"),
    ("Journal scope score and comparison set available", f"{f(SCORED)} papers",
     "Publishing journal had at least 100 articles in the preceding three years"),
    ("Narrowest- or broadest-scope quartile of the comparison set", f"{f(EXTREME)} papers", ""),
    ("Eligible papers", f"{f(ELIGIBLE)} papers",
     f"Broader-scope journals {f(ELIG_BROAD)}; narrower-scope journals {f(ELIG_NARROW)}"),
    ("Primary comparison sample", f"{f(PRIMARY)} papers from {f(PRIMARY_JOURNALS)} journals",
     "Estimated probability of narrower-scope publication between 0.05 and 0.95"),
]
side = [
    ("Excluded", f"{f(BASE - SCORED)} papers", "No reliable journal scope score or no comparison set"),
    ("Excluded", f"{f(SCORED - EXTREME)} papers", "Middle half of the journal-scope distribution"),
    ("Excluded", f"{f(EXTREME - ELIGIBLE)} papers", "Title outside the calibrated range of the Qwen3 classification"),
    ("Excluded", f"{f(ELIGIBLE - PRIMARY)} papers", "Outside common support of the two journal groups"),
]
boxes = []   # (x, y, w, h, title, count, note, fill)
for k, (t, c, n) in enumerate(main):
    boxes.append((MX, TOP + k * (MH + GAP), MW, MH, t, c, n, FILL))
for k, (t, c, n) in enumerate(side):
    y_mid = TOP + (k + 1) * (MH + GAP) - GAP / 2
    boxes.append((SX, y_mid - MH / 2, SW, MH, t, c, n, "#FFFFFF"))
BY = TOP + 5 * (MH + GAP) + 20
BH = 78
boxes.append((MX, BY, MW, BH, "Regenerated comparison sample",
              f"{f(REGEN)} papers from {f(REGEN_JOURNALS)} journals",
              f"Broader-scope {f(REGEN_BROAD)}; narrower-scope {f(REGEN_NARROW)}. Second fit of the same "
              "specification, storing paper-level scores for the year, area, network, and journal-pair analyses", FILL))
boxes.append((SX, BY, SW, BH, "Citations to these papers within five years", f"{f(ALL_EDGES)} citation links",
              f"Same journal or shared author, excluded {f(EXCL_SJ)}; citing paper unclassified {f(UNCLASS)}; "
              f"analyzed {f(INCLUDED)}", "#FFFFFF"))
edges = []   # (x0,y0,x1,y1,dashed[,head])
cx = MX + MW / 2
for k in range(4):
    y0 = TOP + k * (MH + GAP) + MH; y1 = y0 + GAP
    edges.append((cx, y0, cx, y1, False))
    edges.append((cx, y0 + GAP / 2, SX, y0 + GAP / 2, False))
# The regenerated sample branches from the eligible papers, not from the primary sample.
ye = TOP + 3 * (MH + GAP) + MH / 2
edges.append((MX, ye, MX - 24, ye, True, False))
edges.append((MX - 24, ye, MX - 24, BY + BH / 2, True, False))
edges.append((MX - 24, BY + BH / 2, MX, BY + BH / 2, True, True))
edges.append((MX + MW, BY + BH / 2, SX, BY + BH / 2, False))
W, H = SX + SW + 40, BY + BH + 40

# ---- draw.io ----------------------------------------------------------------------------
cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>']
for i, (x, y, w, h, t, c, n, fill) in enumerate(boxes, start=2):
    value = f"<b>{html.escape(t)}</b><br>{html.escape(c)}" + (f"<br><font style=\"font-size: 8px\">{html.escape(n)}</font>" if n else "")
    style = (f"rounded=0;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={FRAME};strokeWidth=1;"
             "fontFamily=Helvetica;fontSize=9;fontColor=#222222;align=left;verticalAlign=top;spacingLeft=6;spacingTop=2;")
    cells.append(f'<mxCell id="b{i}" value="{html.escape(value, quote=True)}" style="{style}" vertex="1" parent="1">'
                 f'<mxGeometry x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" as="geometry"/></mxCell>')
for i, (x0, y0, x1, y1, dashed, *head) in enumerate(edges, start=100):
    head = head[0] if head else True
    style = ((f"endArrow=block;endFill=1;" if head else "endArrow=none;") + f"html=1;strokeColor={FRAME};strokeWidth=1;rounded=0;"
             + ("dashed=1;" if dashed else ""))
    cells.append(f'<mxCell id="e{i}" style="{style}" edge="1" parent="1"><mxGeometry relative="1" as="geometry">'
                 f'<mxPoint x="{x0:g}" y="{y0:g}" as="sourcePoint"/><mxPoint x="{x1:g}" y="{y1:g}" as="targetPoint"/>'
                 '</mxGeometry></mxCell>')
xml = ('<mxfile host="app.diagrams.net"><diagram name="Sample construction" id="s1">'
       f'<mxGraphModel dx="{W}" dy="{H}" grid="1" gridSize="10" guides="1" page="1" pageWidth="{W}" pageHeight="{H}">'
       '<root>' + "".join(cells) + '</root></mxGraphModel></diagram></mxfile>')
(ROOT / "figures" / "supplementary_figure_s1_sample_construction.drawio").write_text(xml)

# ---- PDF/PNG from the same geometry ------------------------------------------------------
fig = plt.figure(figsize=(W / 72, H / 72))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.set_axis_off()
import textwrap
for x, y, w, h, t, c, n, fill in boxes:
    ax.add_patch(Rectangle((x, y), w, h, fc=fill, ec=FRAME, lw=1.0))
    chars = int(w / 4.6)
    ax.text(x + 6, y + 5, "\n".join(textwrap.wrap(t, chars)), fontsize=9, fontweight="bold", va="top", color=INK, linespacing=1.15)
    n_title = len(textwrap.wrap(t, chars))
    ax.text(x + 6, y + 5 + 11.5 * n_title + 1, c, fontsize=9, va="top", color=INK)
    if n:
        ax.text(x + 6, y + 5 + 11.5 * (n_title + 1) + 3, "\n".join(textwrap.wrap(n, int(w / 4.1))), fontsize=8, va="top",
                color=INK, linespacing=1.15)
for x0, y0, x1, y1, dashed, *head in edges:
    head = head[0] if head else True
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>,head_length=0.5,head_width=0.25" if head else "-", color=FRAME, lw=1.0, shrinkA=0, shrinkB=0,
                                ls=(0, (3, 3)) if dashed else "-"))
for suffix in ("pdf", "png"):
    out = ROOT / "figures" / f"supplementary_figure_s1_sample_construction.{suffix}"
    fig.savefig(out, dpi=300 if suffix == "png" else None)
    assert out.stat().st_size > 10_000
    print(f"wrote {out.name}: {out.stat().st_size:,} bytes")
print("wrote supplementary_figure_s1_sample_construction.drawio")
