#!/usr/bin/env python3
"""Supplementary Figure S2: propensity overlap and residual covariate imbalance (primary 63-leaf model)."""
import csv
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "source_data"
BLUE, RED, INK, GREY = "#2E5C9E", "#B23A2A", "#222222", "#8A8A8A"
plt.rcParams.update({"font.family": ["Arial", "Liberation Sans"], "font.size": 7, "pdf.fonttype": 42,
                     "ps.fonttype": 42, "axes.linewidth": 0.6})


def read(name):
    with (DATA / name).open(newline="") as handle:
        return list(csv.DictReader(handle))


bins = read("SourceData_ED2_propensity_bins.csv")
bal = [r for r in read("SourceData_ED2_balance.csv") if r["candidate"] == "primary_leaves_63"]
assert len(bins) == 80


def label(cov):
    fixed = {"lead_prior_venue_specialization": "First-/last-author prior venue scope",
             "lead_prior_venue_specialization__missing": "Author prior venue scope missing",
             "lead_prior_venue_missing": "Author history unavailable",
             "lead_prior_embedding_breadth": "First-/last-author prior content breadth",
             "log1p_prior_prestige": "Journal prior prestige",
             "log1p_institution_mean_prior_citations": "Institution prior citations, mean",
             "log1p_institution_max_prior_citations": "Institution prior citations, max.",
             "log1p_institution_mean_prior_works": "Institution prior works, mean",
             "log1p_institution_max_prior_works": "Institution prior works, max.",
             "log1p_author_mean_prior_citations": "Author prior citations, mean",
             "log1p_author_max_prior_citations": "Author prior citations, max.",
             "choice_prevalence": "Comparison-set share in narrower group",
             "lead_country=__MISSING__": "Lead country not recorded",
             "prior_oa_share": "Journal open-access share",
             "log1p_reference_count": "Reference count", "reference_entropy": "Reference-field entropy"}
    if cov in fixed:
        return fixed[cov]
    if m := re.fullmatch(r"pc(\d+)", cov):
        return f"SPECTER2 title component {int(m.group(1))}"
    if m := re.fullmatch(r"qpc(\d+)", cov):
        return f"Qwen3 title component {int(m.group(1))}"
    if m := re.fullmatch(r"semantic_cluster=(\d+)", cov):
        return f"Topic group {int(m.group(1))} indicator"
    if m := re.fullmatch(r"lead_country=(\w+)", cov):
        return f"Lead country {m.group(1)}"
    if m := re.fullmatch(r"publication_year=(\d+)", cov):
        return f"Publication year {m.group(1)}"
    return cov


fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(7.2, 3.3), gridspec_kw={"width_ratios": [1, 1.1], "wspace": 1.15})

# a: propensity overlap within support
for arm, color in (("Broader scope", BLUE), ("Narrower scope", RED)):
    rows = sorted((r for r in bins if r["arm"] == arm), key=lambda r: float(r["bin_left"]))
    x = np.array([float(r["bin_left"]) for r in rows] + [float(rows[-1]["bin_right"])])
    d = np.array([float(r["density"]) for r in rows])
    ax_a.stairs(d, x, color=color, lw=1.0, label=arm)
ax_a.axvspan(0, 0.05, color="#EEEEEE", lw=0); ax_a.axvspan(0.95, 1, color="#EEEEEE", lw=0)
ax_a.set_xlim(0, 1); ax_a.set_xlabel("Estimated probability of narrower-scope publication")
ax_a.set_ylabel("Density"); ax_a.legend(frameon=False, loc="upper center", fontsize=6.5)
ax_a.spines[["top", "right"]].set_visible(False)
ax_a.set_title("Papers in both journal groups span the\nrange of estimated probabilities", loc="left", fontsize=7)
ax_a.text(0.025, ax_a.get_ylim()[1] * 0.97, "excluded", rotation=90, ha="center", va="top", fontsize=5.5, color=GREY)
ax_a.text(0.975, ax_a.get_ylim()[1] * 0.97, "excluded", rotation=90, ha="center", va="top", fontsize=5.5, color=GREY)

# b: Love plot for the 12 largest weighted residual imbalances, plus the largest raw ones for context
w = {r["covariate"]: float(r["smd"]) for r in bal if r["stage"] == "weighted"}
raw = {r["covariate"]: float(r["smd"]) for r in bal if r["stage"] == "raw"}
top = sorted(w, key=lambda c: -abs(w[c]))[:12]
top = top[::-1]
y = np.arange(len(top))
for k, cov in enumerate(top):
    ax_b.plot([abs(raw[cov]), abs(w[cov])], [k, k], color="#DDDDDD", lw=1.2, zorder=1)
ax_b.scatter([abs(raw[c]) for c in top], y, s=16, color=GREY, zorder=3, label="Unweighted")
ax_b.scatter([abs(w[c]) for c in top], y, s=16, color=RED, marker="s", zorder=4, label="Weighted")
ax_b.axvline(0.10, color=INK, lw=0.6, ls=(0, (3, 2)))
ax_b.set_yticks(y); ax_b.set_yticklabels([label(c) for c in top], fontsize=6.2)
ax_b.set_xlabel("Absolute standardized mean difference")
ax_b.set_xlim(0, max(abs(raw[c]) for c in top) * 1.08)
ax_b.legend(frameon=False, loc="lower right", fontsize=6.5)
ax_b.spines[["top", "right"]].set_visible(False)
ax_b.set_title("Twelve largest residual differences after weighting", loc="left", fontsize=7)
n_over = sum(abs(v) > 0.10 for v in w.values())
print(f"weighted |SMD|>0.10: {n_over} of {len(w)} covariates; max {max(abs(v) for v in w.values()):.4f}")

fig.text(0.01, 0.97, "a", fontsize=10, fontweight="bold")
fig.text(0.44, 0.97, "b", fontsize=10, fontweight="bold")
fig.subplots_adjust(left=0.07, right=0.99, bottom=0.17, top=0.86)
for suffix in ("pdf", "png"):
    out = ROOT / "figures" / f"supplementary_figure_s2_balance.{suffix}"
    fig.savefig(out, dpi=300 if suffix == "png" else None)
    assert out.stat().st_size > 10_000
    print(f"wrote {out.name}: {out.stat().st_size:,} bytes")
